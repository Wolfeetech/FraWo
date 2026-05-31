"""Community API endpoints — votes, chat, song requests."""

from datetime import datetime, timedelta, timezone
from typing import List
import xmlrpc.client

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import get_db
from app.models.community import ChatMessage, TrackVote, CommunityMember
from app.models.track import Track
from app.models.station import Station

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
    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
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
        default_listen = _public_url(data["station"]["listen_url"]) or ""

        # Build explicit mount URLs — robust regardless of what AzuraCast returns as default
        base = "https://funk.frawo-tech.de/listen/frawo_funk"
        standard_url = f"{base}/radio.mp3"
        hifi_url = f"{base}/hifi.mp3"

        return {
            "title": data["now_playing"]["song"]["title"],
            "artist": data["now_playing"]["song"]["artist"],
            "album": data["now_playing"]["song"]["album"],
            "art": _public_url(data["now_playing"]["song"].get("art")),
            "listeners": data["listeners"]["current"],
            "elapsed": data["now_playing"].get("elapsed", 0),
            "duration": data["now_playing"]["song"].get("length", 0),
            # Legacy key — keep for backward compat, points to standard
            "stream_url": standard_url,
            # Explicit quality streams
            "standard_stream_url": standard_url,
            "hifi_stream_url": hifi_url,
            "station": data["station"]["name"],
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
                    'description': f"Hörer hat sich über das Webradio funk.frawo-tech.de registriert.\nZugangscode: {token}"
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


def _generate_access_token() -> str:
    import secrets
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "FW-" + "".join(secrets.choice(chars) for _ in range(6))


@router.post("/register", summary="Register or update a community member (Lead Acquisition)")
async def register_member(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    nickname = (body.get("nickname") or "").strip()
    if not nickname or len(nickname) > 50:
        raise HTTPException(status_code=422, detail="nickname must be 1-50 chars")
    
    email = (body.get("email") or "").strip()
    if email and (len(email) > 100 or "@" not in email):
        raise HTTPException(status_code=422, detail="email is invalid")

    client_id = _client_id(request)
    candidate_token = _generate_access_token()

    # Odoo SSOT Sync & Lead Generation
    odoo_res = odoo_register_or_get_partner(nickname, email if email else None, candidate_token)
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


@router.post("/set_supporter", summary="Mark a client as a verified supporter")
async def set_supporter(request: Request, db: AsyncSession = Depends(get_db)):
    client_id = _client_id(request)
    res = await db.execute(
        select(CommunityMember).where(CommunityMember.client_id == client_id)
    )
    member = res.scalar_one_or_none()

    if not member:
        # Default guest supporter
        token = _generate_access_token()
        odoo_register_or_get_partner("Underground Supporter", None, token)
        odoo_set_partner_supporter(token)
        member = CommunityMember(
            client_id=client_id,
            nickname="Underground Supporter",
            email=None,
            is_supporter=True,
            access_token=token,
        )
        db.add(member)
    else:
        member.is_supporter = True
        if member.access_token:
            odoo_set_partner_supporter(member.access_token)

    await db.commit()
    await db.refresh(member)

    return {
        "status": "success",
        "nickname": member.nickname,
        "is_supporter": member.is_supporter,
        "access_token": member.access_token,
    }


@router.post("/login", summary="Login/Reclaim session with an access token")
async def login_member(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    token = (body.get("access_token") or "").strip().upper()
    if not token:
        raise HTTPException(status_code=422, detail="access_token is required")

    # Query Odoo SSOT for session recovery
    odoo_partner = odoo_get_partner_by_token(token)
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


# --- Song requests (proxy to AzuraCast) ---

@router.get("/requests/search", summary="Search for requestable tracks")
async def search_requests(q: str):
    if len(q) < 2:
        raise HTTPException(status_code=422, detail="query too short")
    try:
        data = await _azuracast_get(
            f"/api/station/{settings.azuracast_station_id}/requests?search={q}"
        )
        return data
    except Exception as exc:
        logger.warning("request_search_failed", error=str(exc))
        raise HTTPException(status_code=503, detail="Search unavailable")


@router.post("/requests/{request_id}", summary="Submit a song request")
async def submit_request(request_id: str):
    try:
        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
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
