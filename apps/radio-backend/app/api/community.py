"""Community API endpoints — votes, chat, song requests."""

import asyncio
import secrets
from collections import defaultdict
from datetime import date as _date, datetime, timedelta, timezone
from typing import List
import xmlrpc.client

import httpx
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import get_db
from app.models.community import ChatMessage, TrackVote, CommunityMember
from app.models.track import Track
from app.models.station import Station

# --- Redis-backed rate limiter (falls back to in-memory if Redis unavailable) ---
# Multi-worker safe: each worker shares the same Redis counter.
# In-memory fallback: per-worker, so limits are multiplied by worker count (acceptable degradation).
_rate_buckets: dict[tuple[str, str], list[datetime]] = defaultdict(list)

async def _check_rate(ip: str, endpoint: str, max_calls: int, window_seconds: int) -> None:
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(str(settings.redis_url), socket_connect_timeout=1)
        key = f"rl:{endpoint}:{ip}"
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window_seconds)
        await r.aclose()
        if count > max_calls:
            raise HTTPException(status_code=429, detail="Zu viele Anfragen — bitte warten.")
    except HTTPException:
        raise
    except Exception:
        # Redis unavailable — fall back to in-memory (per-worker, best-effort)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)
        _rate_buckets[(ip, endpoint)] = [t for t in _rate_buckets[(ip, endpoint)] if t > cutoff]
        if len(_rate_buckets[(ip, endpoint)]) >= max_calls:
            raise HTTPException(status_code=429, detail="Zu viele Anfragen — bitte warten.")
        _rate_buckets[(ip, endpoint)].append(now)

logger = get_logger(__name__)

router = APIRouter(prefix="/community", tags=["Community"])

AZURACAST_BASE = str(settings.azuracast_api_url).rstrip("/").removesuffix("/api")
AZURACAST_PUBLIC = "https://funk.frawo-tech.de"


def _public_url(url: str | None) -> str | None:
    """Rewrite internal AzuraCast URLs to public domain."""
    if not url:
        return url
    for prefix in ("http://172.20.0.1", "http://localhost", "http://azuracast"):
        if url.startswith(prefix):
            return AZURACAST_PUBLIC + url[len(prefix):]
    return url


def _azura_headers() -> dict:
    key = getattr(settings, "azuracast_api_key", None)
    return {"X-API-Key": key} if key else {}


async def _azuracast_get(path: str) -> dict:
    async with httpx.AsyncClient(verify=settings.azuracast_verify_ssl, timeout=5.0) as client:
        resp = await client.get(f"{AZURACAST_BASE}{path}", headers=_azura_headers())
        resp.raise_for_status()
        return resp.json()


def _client_id(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    return ip


# --- Now Playing (direct AzuraCast proxy) ---

@router.get("/nowplaying", summary="Live now-playing from AzuraCast")
async def nowplaying():
    try:
        data = await _azuracast_get(f"/api/nowplaying/{settings.azuracast_station_id}")

        # Build explicit mount URLs — robust regardless of what AzuraCast returns as default
        base = "https://funk.frawo-tech.de/listen/frawo_funk"
        standard_url = f"{base}/radio.mp3"
        hifi_url = f"{base}/hifi.mp3"

        # Clean up title — AzuraCast sometimes concatenates multiple versions with semicolons
        raw_title = data["now_playing"]["song"]["title"] or ""
        clean_title = raw_title.split(";")[0].strip()

        # Extract show name from playlist field ("Show: Bodensee Sunrise (Chill)" → "Bodensee Sunrise (Chill)")
        raw_playlist = data["now_playing"].get("playlist", "") or ""
        show_name = raw_playlist.removeprefix("Show: ").strip() if raw_playlist else None

        # Fetch next show from schedule
        next_show = None
        try:
            schedule = await _azuracast_get(f"/api/station/{settings.azuracast_station_id}/schedule")
            if isinstance(schedule, list):
                upcoming = [s for s in schedule if not s.get("is_now") and s.get("name", "").startswith("Show:")]
                if upcoming:
                    s = upcoming[0]
                    next_show = {
                        "name": s["name"].removeprefix("Show: ").strip(),
                        "start_timestamp": s.get("start_timestamp"),
                    }
        except Exception:
            pass

        return {
            "title": clean_title,
            "artist": data["now_playing"]["song"]["artist"],
            "album": data["now_playing"]["song"]["album"],
            "art": _public_url(data["now_playing"]["song"].get("art")),
            "listeners": data["listeners"]["current"],
            "elapsed": data["now_playing"].get("elapsed", 0),
            "duration": data["now_playing"]["song"].get("length", 0),
            "stream_url": standard_url,
            "standard_stream_url": standard_url,
            "hifi_stream_url": hifi_url,
            "station": data["station"]["name"],
            "show": show_name,
            "next_show": next_show,
        }
    except Exception as exc:
        logger.warning("azuracast_nowplaying_failed", error=str(exc))
        raise HTTPException(status_code=503, detail="AzuraCast unreachable")



# --- Votes ---

@router.post("/vote", summary="Vote on current track")
async def vote(
    request: Request,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    await _check_rate(_client_id(request), "vote", max_calls=10, window_seconds=60)
    reaction = body.get("reaction")
    if reaction not in ("up", "down"):
        raise HTTPException(status_code=422, detail="reaction must be 'up' or 'down'")

    track_key = body.get("track_key", "")
    client_id = _client_id(request)

    # 1. Update or create TrackVote
    existing = await db.execute(
        select(TrackVote).where(
            TrackVote.track_key == track_key,
            TrackVote.client_id == client_id,
        )
    )
    vote_row = existing.scalar_one_or_none()

    if vote_row:
        vote_row.reaction = reaction
    else:
        db.add(TrackVote(track_key=track_key, client_id=client_id, reaction=reaction))

    await db.commit()

    # 2. Get vote counts
    counts = await db.execute(
        select(TrackVote.reaction, func.count(TrackVote.id))
        .where(TrackVote.track_key == track_key)
        .group_by(TrackVote.reaction)
    )
    tally = {row[0]: row[1] for row in counts}
    up_votes = tally.get("up", 0)
    down_votes = tally.get("down", 0)

    # 3. Synchronize with "tracks" table for curation
    try:
        artist, title = "", ""
        if "|" in track_key:
            parts = track_key.split("|", 1)
            artist, title = parts[0].strip(), parts[1].strip()
        else:
            artist, title = "Unknown", track_key.strip()

        # Ensure a default station exists
        station_res = await db.execute(select(Station).where(Station.id == 1))
        station_row = station_res.scalar_one_or_none()
        if not station_row:
            station_row = Station(
                id=1,
                name="FraWo Funk",
                slug="frawo-funk",
                stream_url="https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3",
                nowplaying_url="http://172.20.0.1/api/nowplaying/1",
                is_active=True,
                is_online=True,
            )
            db.add(station_row)
            await db.commit()

        # Find or create track
        track_res = await db.execute(
            select(Track).where(
                Track.artist == artist,
                Track.title == title,
            )
        )
        track_row = track_res.scalar_one_or_none()

        if not track_row:
            track_row = Track(
                artist=artist,
                title=title,
                station_id=1,
                rating_count=up_votes + down_votes,
                average_rating=float(up_votes - down_votes),
            )
            db.add(track_row)
        else:
            track_row.rating_count = up_votes + down_votes
            track_row.average_rating = float(up_votes - down_votes)

        await db.commit()
    except Exception as exc:
        logger.error("sync_track_rating_failed", error=str(exc))

    # System chat — throttled, uses member nickname if registered
    member_res = await db.execute(
        select(CommunityMember.nickname).where(CommunityMember.client_id == client_id)
    )
    nickname = member_res.scalar_one_or_none() or "Anonym"
    await _vote_chat_throttled(db, track_key, nickname, reaction)

    return {"up": up_votes, "down": down_votes, "your_vote": reaction}


@router.get("/votes/{track_key}", summary="Get vote tally for a track")
async def get_votes(track_key: str, request: Request, db: AsyncSession = Depends(get_db)):
    counts = await db.execute(
        select(TrackVote.reaction, func.count(TrackVote.id))
        .where(TrackVote.track_key == track_key)
        .group_by(TrackVote.reaction)
    )
    tally = {row[0]: row[1] for row in counts}
    client_id = _client_id(request)
    mine = await db.execute(
        select(TrackVote.reaction).where(
            TrackVote.track_key == track_key,
            TrackVote.client_id == client_id,
        )
    )
    my_vote = mine.scalar_one_or_none()
    return {"up": tally.get("up", 0), "down": tally.get("down", 0), "your_vote": my_vote}


# --- Chat ---

@router.get("/chat", response_model=List[dict], summary="Get recent chat messages")
async def get_chat(db: AsyncSession = Depends(get_db), limit: int = 50):
    result = await db.execute(
        select(ChatMessage, CommunityMember.is_supporter)
        .outerjoin(CommunityMember, ChatMessage.client_id == CommunityMember.client_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": m.id,
            "name": m.display_name,
            "text": m.text,
            "ts": m.created_at.isoformat(),
            "is_supporter": bool(is_supporter),
        }
        for m, is_supporter in reversed(rows)
    ]


@router.post("/chat", summary="Post a chat message")
async def post_chat(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    text_content = (body.get("text") or "").strip()
    if not text_content or len(text_content) > 280:
        raise HTTPException(status_code=422, detail="text must be 1-280 chars")

    client_id = _client_id(request)
    member_res = await db.execute(
        select(CommunityMember).where(CommunityMember.client_id == client_id)
    )
    member = member_res.scalar_one_or_none()
    
    if member:
        name = member.nickname
    else:
        name = "Anonym"

    cutoff = datetime.now(timezone.utc) - timedelta(seconds=10)
    flood = await db.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.client_id == client_id,
            ChatMessage.created_at > cutoff,
        )
    )
    if (flood.scalar() or 0) >= 3:
        raise HTTPException(status_code=429, detail="Slow down")

    msg = ChatMessage(
        client_id=client_id,
        display_name=name,
        text=text_content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    
    is_supporter = member.is_supporter if member else False
    return {
        "id": msg.id, 
        "name": msg.display_name, 
        "text": msg.text, 
        "ts": msg.created_at.isoformat(),
        "is_supporter": is_supporter,
    }


# --- Lead Acquisition & Member Management ---

# --- Odoo ERP SSOT Integration & Caching ---

def _get_odoo_client():
    try:
        url = settings.odoo_url
        db = settings.odoo_db
        user = settings.odoo_user
        password = settings.odoo_password
        if not password:
            logger.warning("odoo_password_not_set_in_env")
            return None, None
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, password, {})
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
        return uid, models
    except Exception as exc:
        logger.error("odoo_connection_failed", error=str(exc))
        return None, None

def odoo_register_or_get_partner(nickname: str, email: str | None, token: str) -> dict:
    try:
        uid, models = _get_odoo_client()
        if not uid or not models:
            logger.warning("odoo_offline_fallback_register")
            return {"token": token, "is_supporter": False}

        db = settings.odoo_db
        pw = settings.odoo_password
        partner_id = None
        existing_token = None
        is_supporter = False

        # 1. Search existing partner by email
        if email:
            existing = models.execute_kw(
                db, uid, pw, 'res.partner', 'search_read',
                [[('email', '=', email)]],
                {'fields': ['id', 'name', 'ref', 'comment']}
            )
            if existing:
                partner = existing[0]
                partner_id = partner['id']
                existing_token = partner.get('ref')
                comment = partner.get('comment') or ""
                is_supporter = "supporter" in comment.lower()

                # If partner has no ref, assign the token
                if not existing_token:
                    models.execute_kw(
                        db, uid, pw, 'res.partner', 'write',
                        [[partner_id], {'ref': token}]
                    )
                    existing_token = token
                logger.info("odoo_linked_existing_partner", partner_id=partner_id, email=email)

        # 2. If not found, create new Partner & CRM Lead
        if not partner_id:
            partner_id = models.execute_kw(
                db, uid, pw, 'res.partner', 'create',
                [{
                    'name': nickname,
                    'email': email if email else False,
                    'ref': token,
                    'comment': "Webradio VIP Hörer"
                }]
            )
            logger.info("odoo_created_new_partner", partner_id=partner_id, name=nickname)

            # Create CRM Lead for lead acquisition!
            lead_id = models.execute_kw(
                db, uid, pw, 'crm.lead', 'create',
                [{
                    'name': f"Radio Hörer: {nickname}",
                    'partner_id': partner_id,
                    'email_from': email if email else False,
                    'description': f"Hörer hat sich über funk.frawo-tech.de registriert.\nZugangscode: {token}",
                    'stage_id': 1,
                    'user_id': 6,
                    'tag_ids': [],
                }]
            )
            logger.info("odoo_created_crm_lead", lead_id=lead_id)
            existing_token = token

        return {"token": existing_token, "is_supporter": is_supporter}
    except Exception as exc:
        logger.error("odoo_register_or_get_partner_failed", error=str(exc))
        return {"token": token, "is_supporter": False}

def odoo_get_partner_by_token(token: str) -> dict | None:
    try:
        uid, models = _get_odoo_client()
        if not uid or not models:
            return None

        db = settings.odoo_db
        pw = settings.odoo_password
        partners = models.execute_kw(
            db, uid, pw, 'res.partner', 'search_read',
            [[('ref', '=', token)]],
            {'fields': ['id', 'name', 'email', 'comment']}
        )
        if partners:
            partner = partners[0]
            comment = partner.get('comment') or ""
            is_supporter = "supporter" in comment.lower()
            return {
                "nickname": partner['name'],
                "email": partner['email'] or "",
                "is_supporter": is_supporter
            }
        return None
    except Exception as exc:
        logger.error("odoo_get_partner_by_token_failed", error=str(exc))
        return None

def odoo_set_partner_supporter(token: str) -> bool:
    try:
        uid, models = _get_odoo_client()
        if not uid or not models:
            return False

        db = settings.odoo_db
        pw = settings.odoo_password
        partners = models.execute_kw(
            db, uid, pw, 'res.partner', 'search_read',
            [[('ref', '=', token)]],
            {'fields': ['id', 'comment']}
        )
        if partners:
            partner = partners[0]
            pid = partner['id']
            comment = partner.get('comment') or ""
            if "supporter" not in comment.lower():
                new_comment = (comment.strip() + " [supporter]").strip()
                models.execute_kw(
                    db, uid, pw, 'res.partner', 'write',
                    [[pid], {'comment': new_comment}]
                )
            return True
        return False
    except Exception as exc:
        logger.error("odoo_set_partner_supporter_failed", error=str(exc))
        return False


async def _system_chat(db: AsyncSession, text: str) -> None:
    """Post a system event message to chat. Silently skips on error."""
    try:
        db.add(ChatMessage(client_id="__system__", display_name="FraWo Funk", text=text))
        await db.commit()
    except Exception as exc:
        logger.warning("system_chat_failed", error=str(exc))


async def _vote_chat_throttled(db: AsyncSession, track_key: str, nickname: str, reaction: str) -> None:
    """Post a vote event to chat — max once per track per 90 seconds to avoid spam."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=90)
    recent = await db.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.client_id == "__system__",
            ChatMessage.text.like(f"%{track_key[:40]}%"),
            ChatMessage.created_at > cutoff,
        )
    )
    if (recent.scalar() or 0) == 0:
        parts = track_key.split("|", 1)
        artist = parts[0].strip() if len(parts) > 1 else ""
        title = (parts[1] if len(parts) > 1 else parts[0]).split(";")[0].strip()[:50]
        label = f"{artist} — {title}" if artist else title
        emoji = "🔥" if reaction == "up" else "💀"
        await _system_chat(db, f"{emoji} {nickname.upper()} — {label}")


def _generate_access_token() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "FW-" + "".join(secrets.choice(chars) for _ in range(6))


def odoo_record_donation(partner_id: int, amount: float, token: str, nickname: str) -> int | None:
    """Create a pending donation lead in Odoo CRM and return the lead ID."""
    try:
        uid, models = _get_odoo_client()
        if not uid or not models:
            return None
        db = settings.odoo_db
        pw = settings.odoo_password
        lead_id = models.execute_kw(
            db, uid, pw, 'crm.lead', 'create',
            [{
                'name': f"Supporter-Beitrag €{amount:.0f} — {nickname}",
                'partner_id': partner_id,
                'stage_id': 1,
                'user_id': 6,
                'description': (
                    f"Freiwilliger Supporter-Beitrag via funk.frawo-tech.de\n"
                    f"Betrag: €{amount:.2f}\n"
                    f"Zugangscode: {token}\n"
                    f"Status: AUSSTEHEND — Eingang manuell prüfen (PayPal PPWP)"
                ),
                'tag_ids': [],
            }]
        )
        logger.info("odoo_donation_lead_created", lead_id=lead_id, amount=amount, token=token)
        return lead_id
    except Exception as exc:
        logger.error("odoo_record_donation_failed", error=str(exc))
        return None


def odoo_confirm_donation(token: str, amount: float | None = None) -> bool:
    """Confirm donation: create invoice, register PayPal payment, send receipt email."""
    try:
        uid, models = _get_odoo_client()
        if not uid or not models:
            return False
        db = settings.odoo_db
        pw = settings.odoo_password
        today = _date.today().isoformat()

        # Find partner by token
        partners = models.execute_kw(
            db, uid, pw, 'res.partner', 'search_read',
            [[('ref', '=', token)]],
            {'fields': ['id', 'name', 'email', 'comment']}
        )
        if not partners:
            return False

        partner = partners[0]
        pid = partner['id']
        name = partner['name']
        email = partner['email']
        amount_val = amount or 0.0

        # Mark as supporter in partner comment
        comment = partner.get('comment') or ""
        if "supporter" not in comment.lower():
            models.execute_kw(db, uid, pw, 'res.partner', 'write',
                [[pid], {'comment': (comment.strip() + " [supporter]").strip()}])

        # Update ALL pending donation leads for this partner to Won
        leads = models.execute_kw(
            db, uid, pw, 'crm.lead', 'search_read',
            [[('partner_id', '=', pid), ('stage_id', '=', 1), ('name', 'like', 'Supporter-Beitrag')]],
            {'fields': ['id']}
        )
        if leads:
            all_ids = [l['id'] for l in leads]
            models.execute_kw(db, uid, pw, 'crm.lead', 'write',
                [all_ids, {
                    'stage_id': 4,
                    'description': f"Beitrag bestätigt\nZugangscode: {token}\nBetrag: €{amount_val:.2f}",
                }])

        # Create invoice + register PayPal payment
        invoice_id = models.execute_kw(db, uid, pw, 'account.move', 'create', [{
            'move_type': 'out_invoice',
            'partner_id': pid,
            'invoice_date': today,
            'journal_id': 1,  # Customer Invoices (payment registered separately via PPWP)
            'invoice_line_ids': [(0, 0, {
                'name': 'Freiwilliger Supporter-Beitrag — FraWo Funk',
                'quantity': 1.0,
                'price_unit': amount_val,
                'account_id': 24,  # 400000 Product Sales
            })],
            'narration': f'Supporter-Beitrag (Trinkgeld) via PayPal. Zugangscode: {token}',
        }])
        models.execute_kw(db, uid, pw, 'account.move', 'action_post', [[invoice_id]])
        inv = models.execute_kw(db, uid, pw, 'account.move', 'read',
            [[invoice_id]], {'fields': ['name']})[0]
        invoice_number = inv['name']

        payment_id = models.execute_kw(db, uid, pw, 'account.payment.register', 'create', [{
            'journal_id': 8,
            'payment_date': today,
            'amount': amount_val,
            'communication': f'Supporter-Beitrag {name} {token}',
        }], {'context': {'active_model': 'account.move', 'active_ids': [invoice_id]}})
        models.execute_kw(db, uid, pw, 'account.payment.register', 'action_create_payments',
            [[payment_id]], {'context': {'active_model': 'account.move', 'active_ids': [invoice_id]}})

        logger.info("odoo_invoice_created", invoice=invoice_number, token=token, amount=amount_val)

        # Send receipt email
        if email:
            amount_str = f"€{amount_val:.2f}"
            body = (
                f"<p>Hallo {name},</p>"
                f"<hr>"
                f"<p><strong>Zahlungsbestätigung</strong><br>"
                f"FraWo GbR — funk.frawo-tech.de<br>"
                f"Datum: {today}<br>"
                f"Beleg-Nr.: {invoice_number}<br>"
                f"Betrag: <strong>{amount_str}</strong><br>"
                f"Verwendungszweck: Freiwilliger Supporter-Beitrag (Trinkgeld)<br>"
                f"Zahlungsweg: PayPal</p>"
                f"<p><em>Dies ist kein steuerlich abzugsfähiger Betrag.</em></p>"
                f"<hr>"
                f"<p>Du bist jetzt <strong>✦ VIP Supporter</strong> von FraWo Funk!<br>"
                f"Dein Zugangscode: <strong>{token}</strong><br>"
                f"Einlösen auf: <a href='https://funk.frawo-tech.de'>funk.frawo-tech.de</a></p>"
                f"<p>Danke & keep it funky,<br><strong>Wolf — FraWo Funk</strong></p>"
            )
            models.execute_kw(db, uid, pw, 'res.partner', 'message_post', [[pid]], {
                'body': body,
                'message_type': 'email',
                'subtype_xmlid': 'mail.mt_comment',
                'subject': f"Zahlungsbestätigung {invoice_number} — FraWo Funk ✦",
            })
            logger.info("odoo_receipt_sent", partner_id=pid, email=email, invoice=invoice_number)

        return True
    except Exception as exc:
        logger.error("odoo_confirm_donation_failed", error=str(exc))
        return False


@router.post("/register", summary="Register or update a community member (Lead Acquisition)")
async def register_member(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    await _check_rate(_client_id(request), "register", max_calls=5, window_seconds=300)
    nickname = (body.get("nickname") or "").strip()
    if not nickname or len(nickname) > 50:
        raise HTTPException(status_code=422, detail="nickname must be 1-50 chars")
    
    email = (body.get("email") or "").strip()
    if email and (len(email) > 100 or "@" not in email):
        raise HTTPException(status_code=422, detail="email is invalid")

    client_id = _client_id(request)
    candidate_token = _generate_access_token()

    # Odoo SSOT Sync & Lead Generation
    odoo_res = await asyncio.to_thread(odoo_register_or_get_partner, nickname, email if email else None, candidate_token)
    token = odoo_res["token"]
    is_supporter = odoo_res["is_supporter"]

    # Check for existing member in local cache
    res = await db.execute(
        select(CommunityMember).where(CommunityMember.client_id == client_id)
    )
    member = res.scalar_one_or_none()

    if member:
        member.nickname = nickname
        if email:
            member.email = email
        member.access_token = token
        member.is_supporter = is_supporter
    else:
        member = CommunityMember(
            client_id=client_id,
            nickname=nickname,
            email=email if email else None,
            is_supporter=is_supporter,
            access_token=token,
        )
        db.add(member)

    await db.commit()
    await db.refresh(member)

    return {
        "status": "success",
        "nickname": member.nickname,
        "email": member.email,
        "is_supporter": member.is_supporter,
        "access_token": member.access_token,
    }


@router.get("/member_status", summary="Get member status for the current client")
async def get_member_status(request: Request, db: AsyncSession = Depends(get_db)):
    client_id = _client_id(request)
    res = await db.execute(
        select(CommunityMember).where(CommunityMember.client_id == client_id)
    )
    member = res.scalar_one_or_none()

    if member:
        # Proactively ensure cached members have a token
        if not member.access_token:
            member.access_token = _generate_access_token()
            await db.commit()
            await db.refresh(member)

        return {
            "registered": True,
            "nickname": member.nickname,
            "email": member.email,
            "is_supporter": member.is_supporter,
            "access_token": member.access_token,
        }
    else:
        return {
            "registered": False,
        }


def _require_admin(x_admin_key: str = Header(default="")) -> None:
    key = settings.admin_api_key
    if not key or x_admin_key != key:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/donate/initiate", summary="Register donation intent before PayPal redirect (DSGVO-compliant)")
async def donate_initiate(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    """Called before PayPal redirect — records intent, creates Odoo lead."""
    await _check_rate(_client_id(request), "donate", max_calls=3, window_seconds=3600)
    nickname = (body.get("nickname") or "").strip()
    email = (body.get("email") or "").strip()
    amount = body.get("amount")
    consent = body.get("dsgvo_consent", False)

    if not nickname or len(nickname) > 50:
        raise HTTPException(status_code=422, detail="nickname must be 1-50 chars")
    if not email or "@" not in email or len(email) > 100:
        raise HTTPException(status_code=422, detail="Gültige Email-Adresse erforderlich")
    if not consent:
        raise HTTPException(status_code=422, detail="DSGVO-Einwilligung erforderlich")
    if amount not in (2, 5, 10, 2.0, 5.0, 10.0):
        raise HTTPException(status_code=422, detail="Ungültiger Betrag")

    amount = float(amount)
    client_id = _client_id(request)
    candidate_token = _generate_access_token()

    # Register or find partner in Odoo
    odoo_res = await asyncio.to_thread(
        odoo_register_or_get_partner, nickname, email, candidate_token
    )
    token = odoo_res["token"]

    # Find partner_id for the donation lead
    def _get_partner_id(tok: str) -> int | None:
        uid, models = _get_odoo_client()
        if not uid:
            return None
        partners = models.execute_kw(
            settings.odoo_db, uid, settings.odoo_password, 'res.partner', 'search_read',
            [[('ref', '=', tok)]], {'fields': ['id']}
        )
        return partners[0]['id'] if partners else None

    partner_id = await asyncio.to_thread(_get_partner_id, token)
    if partner_id:
        await asyncio.to_thread(odoo_record_donation, partner_id, amount, token, nickname)

    # Upsert local CommunityMember
    res = await db.execute(
        select(CommunityMember).where(CommunityMember.client_id == client_id)
    )
    member = res.scalar_one_or_none()
    if member:
        member.nickname = nickname
        member.email = email
        member.access_token = token
    else:
        member = CommunityMember(
            client_id=client_id,
            nickname=nickname,
            email=email,
            is_supporter=False,
            access_token=token,
        )
        db.add(member)

    await db.commit()
    logger.info("donation_initiated", nickname=nickname, amount=amount, token=token)

    return {
        "status": "pending",
        "access_token": token,
        "amount": amount,
        "message": "Zahlungsabsicht registriert. Nach Bestätigung erhältst du eine Quittung per Email.",
    }


@router.post("/set_supporter", summary="Confirm payment and grant supporter status (admin only)")
async def set_supporter(
    body: dict,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_require_admin),
):
    token = (body.get("access_token") or "").strip().upper()
    if not token:
        raise HTTPException(status_code=422, detail="access_token is required")
    raw_amount = body.get("amount")
    try:
        amount = float(raw_amount) if raw_amount is not None else None
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="amount must be a number")

    res = await db.execute(
        select(CommunityMember).where(CommunityMember.access_token == token)
    )
    member = res.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.is_supporter = True

    # Confirm in Odoo + send email receipt
    await asyncio.to_thread(
        odoo_confirm_donation, token, float(amount) if amount else None
    )

    await db.commit()
    await db.refresh(member)

    await _system_chat(db, f"✦ {member.nickname.upper()} ist jetzt VIP Supporter — Danke fürs Support!")
    logger.info("supporter_confirmed", token=token, amount=amount)
    return {
        "status": "success",
        "nickname": member.nickname,
        "is_supporter": member.is_supporter,
        "access_token": member.access_token,
    }


@router.post("/login", summary="Login/Reclaim session with an access token")
async def login_member(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    await _check_rate(_client_id(request), "login", max_calls=10, window_seconds=300)
    token = (body.get("access_token") or "").strip().upper()
    if not token:
        raise HTTPException(status_code=422, detail="access_token is required")

    # Query Odoo SSOT for session recovery
    odoo_partner = await asyncio.to_thread(odoo_get_partner_by_token, token)
    if not odoo_partner:
        raise HTTPException(status_code=404, detail="Zugangscode ungültig")

    client_id = _client_id(request)

    # Find member by token locally
    res = await db.execute(
        select(CommunityMember).where(CommunityMember.access_token == token)
    )
    member = res.scalar_one_or_none()

    if member:
        # Re-map client ID and sync fresh Odoo details
        member.client_id = client_id
        member.nickname = odoo_partner["nickname"]
        member.email = odoo_partner["email"] if odoo_partner["email"] else None
        member.is_supporter = odoo_partner["is_supporter"]
    else:
        # Delete any conflicting session with this client_id first
        conflict_res = await db.execute(
            select(CommunityMember).where(CommunityMember.client_id == client_id)
        )
        conflict_member = conflict_res.scalar_one_or_none()
        if conflict_member:
            await db.delete(conflict_member)
            await db.commit()

        member = CommunityMember(
            client_id=client_id,
            nickname=odoo_partner["nickname"],
            email=odoo_partner["email"] if odoo_partner["email"] else None,
            is_supporter=odoo_partner["is_supporter"],
            access_token=token,
        )
        db.add(member)

    await db.commit()
    await db.refresh(member)

    return {
        "status": "success",
        "nickname": member.nickname,
        "email": member.email,
        "is_supporter": member.is_supporter,
        "access_token": member.access_token,
    }


# --- Song requests ---
# AzuraCast ignores the ?search= parameter and returns all tracks.
# We cache the full list and filter server-side.
_requests_cache: list = []
_requests_cache_ts: datetime = datetime.min.replace(tzinfo=timezone.utc)
_REQUESTS_CACHE_TTL = 300  # 5 minutes


async def _get_all_requests() -> list:
    global _requests_cache, _requests_cache_ts
    now = datetime.now(timezone.utc)
    if (now - _requests_cache_ts).total_seconds() > _REQUESTS_CACHE_TTL:
        data = await _azuracast_get(f"/api/station/{settings.azuracast_station_id}/requests")
        _requests_cache = data if isinstance(data, list) else data.get("result", [])
        _requests_cache_ts = now
        logger.info("requests_cache_refreshed", count=len(_requests_cache))
    return _requests_cache


@router.get("/requests/search", summary="Search for requestable tracks")
async def search_requests(q: str):
    if len(q) < 2:
        raise HTTPException(status_code=422, detail="query too short")
    try:
        all_tracks = await _get_all_requests()
        ql = q.lower()

        def score(item: dict) -> int:
            song = item.get("song", {})
            title = (song.get("title") or "").lower()
            artist = (song.get("artist") or "").lower()
            text = (song.get("text") or "").lower()
            combined = f"{artist} {title} {text}"
            if ql == title or ql == artist:
                return 0
            if title.startswith(ql) or artist.startswith(ql):
                return 1
            if ql in title or ql in artist:
                return 2
            if ql in combined:
                return 3
            return 99

        results = [t for t in all_tracks if score(t) < 99]
        results.sort(key=score)
        return results[:10]
    except Exception as exc:
        logger.warning("request_search_failed", error=str(exc))
        raise HTTPException(status_code=503, detail="Search unavailable")


@router.post("/requests/{request_id}", summary="Submit a song request")
async def submit_request(request_id: str):
    try:
        async with httpx.AsyncClient(verify=settings.azuracast_verify_ssl, timeout=5.0) as client:
            resp = await client.post(
                f"{AZURACAST_BASE}/api/station/{settings.azuracast_station_id}/request/{request_id}",
                headers=_azura_headers(),
            )
            if resp.status_code == 200:
                return {"status": "queued"}
            return {"status": "error", "detail": resp.text[:200]}
    except Exception as exc:
        logger.warning("request_submit_failed", error=str(exc))
        raise HTTPException(status_code=503, detail="Request unavailable")


# --- Admin / Curation ---

@router.post("/admin/curate", summary="Auto-curate poor rated tracks")
async def auto_curate(request: Request, db: AsyncSession = Depends(get_db)):
    """Find tracks with average_rating <= -3 and remove them from AzuraCast playlists."""
    admin_secret = request.headers.get("X-Admin-Token")
    if admin_secret != settings.secret_key:
        raise HTTPException(status_code=403, detail="Invalid admin token")

    bad_tracks_res = await db.execute(
        select(Track).where(Track.average_rating <= -3.0)
    )
    bad_tracks = bad_tracks_res.scalars().all()
    
    if not bad_tracks:
        return {"status": "ok", "message": "No tracks to curate", "curated": 0}

    curated_count = 0
    errors = []

    async with httpx.AsyncClient(verify=settings.azuracast_verify_ssl, timeout=10.0) as client:
        try:
            resp = await client.get(f"{AZURACAST_BASE}/api/station/{settings.azuracast_station_id}/files", headers=_azura_headers())
            if resp.status_code == 403:
                return {"status": "error", "message": "AzuraCast API Key lacks 'Manage Station Media' permission."}
            resp.raise_for_status()
            files_data = resp.json()
            
            for track in bad_tracks:
                target_file = None
                for f in files_data:
                    if track.azuracast_media_id and f.get("unique_id") == track.azuracast_media_id:
                        target_file = f
                        break
                    if f.get("custom_fields", {}).get("artist") == track.artist and f.get("custom_fields", {}).get("title") == track.title:
                        target_file = f
                        break
                
                if target_file:
                    media_id = target_file.get("id")
                    if media_id:
                        update_payload = {"playlists": []} 
                        update_resp = await client.put(
                            f"{AZURACAST_BASE}/api/station/{settings.azuracast_station_id}/file/{media_id}",
                            json=update_payload,
                            headers=_azura_headers()
                        )
                        if update_resp.status_code in (200, 204):
                            curated_count += 1
                            track.average_rating = 0
                            track.rating_count = 0
                        else:
                            errors.append(f"Failed to update {track.title}: {update_resp.status_code}")
                else:
                    errors.append(f"File not found in Azuracast for {track.artist} - {track.title}")
            
            await db.commit()
            
        except Exception as e:
            logger.error("curate_failed", error=str(e))
            raise HTTPException(status_code=500, detail=f"Curation failed: {str(e)}")

    return {
        "status": "ok",
        "message": f"Curated {curated_count} tracks.",
        "curated": curated_count,
        "errors": errors
    }

