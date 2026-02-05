"""API tests for Clora service."""

import pytest
from httpx import ASGITransport, AsyncClient

from clora.main import app
from clora.db.database import init_db


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db():
    """Initialize database before tests."""
    await init_db()
    yield


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client(client):
    """Create authenticated test client."""
    # Register user
    await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        },
    )

    # Login
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    token = response.json()["access_token"]

    # Return client with auth header
    client.headers["Authorization"] = f"Bearer {token}"
    return client


class TestHealth:
    """Health endpoint tests."""

    async def test_health(self, client):
        """Test health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_root(self, client):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "Clora" in response.json()["service"]


class TestAuth:
    """Authentication tests."""

    async def test_register(self, client):
        """Test user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "newpass123",
            },
        )
        assert response.status_code == 200
        assert response.json()["email"] == "newuser@example.com"

    async def test_register_duplicate_email(self, client):
        """Test duplicate email registration."""
        # First registration
        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "pass123",
            },
        )

        # Second registration with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "pass123",
            },
        )
        assert response.status_code == 400

    async def test_login(self, client):
        """Test user login."""
        # Register
        await client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "loginpass123",
            },
        )

        # Login
        response = await client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "loginpass123",
            },
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register
        await client.post(
            "/auth/register",
            json={
                "email": "wrongpass@example.com",
                "username": "wrongpassuser",
                "password": "correctpass",
            },
        )

        # Login with wrong password
        response = await client.post(
            "/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401


class TestExperts:
    """Expert endpoint tests."""

    async def test_list_experts(self, client):
        """Test listing experts."""
        response = await client.get("/experts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_expert_not_found(self, client):
        """Test getting non-existent expert."""
        response = await client.get("/experts/99999")
        assert response.status_code == 404


class TestMemories:
    """Memory endpoint tests."""

    async def test_list_memories(self, auth_client):
        """Test listing memories."""
        response = await auth_client.get("/memories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_memory(self, auth_client):
        """Test creating a memory."""
        response = await auth_client.post(
            "/memories",
            json={
                "title": "Test Memory",
                "content": "This is a test memory content",
                "category": "test",
                "importance": 5,
            },
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test Memory"

    async def test_search_memories(self, auth_client):
        """Test searching memories."""
        # Create a memory first
        await auth_client.post(
            "/memories",
            json={
                "title": "Searchable Memory",
                "content": "This memory is about startup funding",
                "category": "startup",
            },
        )

        # Search
        response = await auth_client.post(
            "/memories/search",
            json={
                "query": "startup funding",
                "n_results": 5,
            },
        )
        assert response.status_code == 200
        assert "results" in response.json()
