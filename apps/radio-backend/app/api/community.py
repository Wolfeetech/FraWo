"""Community API endpoints — votes, chat, song requests."""

from datetime import datetime, timedelta, timezone
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import get_db
from app.models.community import ChatMessage, TrackVote

logger = get_logger(__name__)

router = APIRouter(prefix="/community", tags=["Community"])

AZURACAST_BASE = str(settings.azuracast_api_url).rstrip("/").removesuffix("/api")


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
        return {
            "title": data["now_playing"]["song"]["title"],
            "artist": data["now_playing"]["song"]["artist"],
            "album": data["now_playing"]["song"]["album"],
            "art": data["now_playing"]["song"].get("art"),
            "listeners": data["listeners"]["current"],
            "elapsed": data["now_playing"].get("elapsed", 0),
            "duration": data["now_playing"]["song"].get("length", 0),
            "stream_url": data["station"]["listen_url"],
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

    counts = await db.execute(
        select(TrackVote.reaction, func.count(TrackVote.id))
        .where(TrackVote.track_key == track_key)
        .group_by(TrackVote.reaction)
    )
    tally = {row[0]: row[1] for row in counts}
    return {"up": tally.get("up", 0), "down": tally.get("down", 0), "your_vote": reaction}


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
        select(ChatMessage).order_by(desc(ChatMessage.created_at)).limit(limit)
    )
    msgs = result.scalars().all()
    return [
        {
            "id": m.id,
            "name": m.display_name,
            "text": m.text,
            "ts": m.created_at.isoformat(),
        }
        for m in reversed(msgs)
    ]


@router.post("/chat", summary="Post a chat message")
async def post_chat(request: Request, body: dict, db: AsyncSession = Depends(get_db)):
    text_content = (body.get("text") or "").strip()
    if not text_content or len(text_content) > 280:
        raise HTTPException(status_code=422, detail="text must be 1-280 chars")
    name = (body.get("name") or "Anonym").strip()[:50]

    cutoff = datetime.now(timezone.utc) - timedelta(seconds=10)
    flood = await db.execute(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.client_id == _client_id(request),
            ChatMessage.created_at > cutoff,
        )
    )
    if (flood.scalar() or 0) >= 3:
        raise HTTPException(status_code=429, detail="Slow down")

    msg = ChatMessage(
        client_id=_client_id(request),
        display_name=name,
        text=text_content,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"id": msg.id, "name": msg.display_name, "text": msg.text, "ts": msg.created_at.isoformat()}


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
