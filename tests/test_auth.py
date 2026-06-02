import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "email": "test@pandoo.com",
            "password": "motdepasse123"
        })
    assert response.status_code == 200
    assert response.json()["email"] == "test@pandoo.com"
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_register_duplicate_email():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "double@pandoo.com",
            "password": "motdepasse123"
        })
        response = await client.post("/auth/register", json={
            "email": "double@pandoo.com",
            "password": "motdepasse123"
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email déjà utilisé"

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "login@pandoo.com",
            "password": "motdepasse123"
        })
        response = await client.post("/auth/login", json={
            "email": "login@pandoo.com",
            "password": "motdepasse123"
        })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "login@pandoo.com",
            "password": "mauvaismdp"
        })
    assert response.status_code == 401