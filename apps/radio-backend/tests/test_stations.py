"""Tests for station endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Station


@pytest.mark.asyncio
async def test_list_stations_empty(client: AsyncClient) -> None:
    """Test listing stations when database is empty."""
    response = await client.get("/api/stations/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_station(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test creating a new station."""
    station_data = {
        "name": "FraWo Funk",
        "slug": "frawo-funk",
        "description": "The best radio in town",
        "stream_url": "http://example.com/stream.mp3",
        "nowplaying_url": "http://example.com/api/nowplaying",
        "location": "Rothkreuz",
        "icon": "📻",
        "color": "#667eea",
    }

    response = await client.post("/api/stations/", json=station_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == station_data["name"]
    assert data["slug"] == station_data["slug"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_duplicate_slug(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test that duplicate slugs are rejected."""
    station_data = {
        "name": "Station 1",
        "slug": "test-station",
        "stream_url": "http://example.com/stream.mp3",
        "nowplaying_url": "http://example.com/api/nowplaying",
    }

    # Create first station
    response1 = await client.post("/api/stations/", json=station_data)
    assert response1.status_code == 201

    # Try to create duplicate
    station_data["name"] = "Station 2"
    response2 = await client.post("/api/stations/", json=station_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_get_station(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test getting a station by ID."""
    # Create station first
    station = Station(
        name="Test Station",
        slug="test-station",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
    )
    test_db.add(station)
    await test_db.commit()
    await test_db.refresh(station)

    # Get station
    response = await client.get(f"/api/stations/{station.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == station.id
    assert data["name"] == station.name


@pytest.mark.asyncio
async def test_get_nonexistent_station(client: AsyncClient) -> None:
    """Test getting a station that doesn't exist."""
    response = await client.get("/api/stations/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_station_by_slug(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test getting a station by slug."""
    station = Station(
        name="Test Station",
        slug="test-station",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
    )
    test_db.add(station)
    await test_db.commit()
    await test_db.refresh(station)

    response = await client.get(f"/api/stations/slug/{station.slug}")
    assert response.status_code == 200
    assert response.json()["slug"] == station.slug


@pytest.mark.asyncio
async def test_update_station(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test updating a station."""
    station = Station(
        name="Old Name",
        slug="test-station",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
    )
    test_db.add(station)
    await test_db.commit()
    await test_db.refresh(station)

    update_data = {"name": "New Name", "description": "Updated description"}

    response = await client.patch(f"/api/stations/{station.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_station(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test deleting a station."""
    station = Station(
        name="Test Station",
        slug="test-station",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
    )
    test_db.add(station)
    await test_db.commit()
    await test_db.refresh(station)

    response = await client.delete(f"/api/stations/{station.id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/stations/{station.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_active_stations_only(client: AsyncClient, test_db: AsyncSession) -> None:
    """Test filtering stations by active status."""
    # Create active station
    active_station = Station(
        name="Active Station",
        slug="active",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
        is_active=True,
    )
    test_db.add(active_station)

    # Create inactive station
    inactive_station = Station(
        name="Inactive Station",
        slug="inactive",
        stream_url="http://example.com/stream.mp3",
        nowplaying_url="http://example.com/api/nowplaying",
        is_active=False,
    )
    test_db.add(inactive_station)

    await test_db.commit()

    # Get only active stations
    response = await client.get("/api/stations/?active_only=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "active"
