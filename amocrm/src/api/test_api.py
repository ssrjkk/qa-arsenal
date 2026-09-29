"""API tests - working examples."""

import pytest
from pydantic import BaseModel


pytestmark = pytest.mark.api


class TestHealth:
    """Health check tests."""

    def test_health_endpoint(self, api_client):
        """Health check returns 200."""
        response = api_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestCreateUser:
    """User creation tests."""

    def test_create_user_success(self, api_client, test_user_data):
        """Create user - successful."""
        response = api_client.post("/api/users", json=test_user_data)

        assert response.status_code == 201

        data = response.json()
        assert "user" in data
        assert data["user"]["name"] == test_user_data["name"]
        assert data["user"]["email"] == test_user_data["email"]
        assert "id" in data["user"]

    def test_create_user_validation_pydantic(self, api_client):
        """Validate response with Pydantic."""

        class UserModel(BaseModel):
            id: int
            name: str
            email: str

        response = api_client.post("/api/users", json={"name": "Valid User", "email": "valid@test.com"})

        if response.status_code == 201:
            data = response.json()["user"]
            user = UserModel(**data)
            assert user.id > 0
            assert user.name == "Valid User"

    def test_create_user_missing_name(self, api_client):
        """Create user without name - 400."""
        response = api_client.post("/api/users", json={"email": "test@test.com"})
        assert response.status_code == 400

    def test_create_user_missing_email(self, api_client):
        """Create user without email - 400."""
        response = api_client.post("/api/users", json={"name": "Test"})
        assert response.status_code == 400

    def test_create_user_empty_body(self, api_client):
        """Create user with empty body - 400."""
        response = api_client.post("/api/users", json={})
        assert response.status_code == 400


class TestUserCRUD:
    """User CRUD tests."""

    def test_get_user(self, api_client, created_user):
        """Get user by ID."""
        if not created_user:
            pytest.skip("User not created")

        response = api_client.get(f"/api/users/{created_user}")
        assert response.status_code == 200

        data = response.json()
        assert "user" in data
        assert data["user"]["id"] == created_user

    def test_get_user_not_found(self, api_client):
        """Get non-existent user - 404."""
        response = api_client.get("/api/users/999999999")
        assert response.status_code == 404

    def test_update_user(self, api_client, created_user):
        """Update user."""
        if not created_user:
            pytest.skip("User not created")

        response = api_client.put(f"/api/users/{created_user}", json={"name": "Updated Name"})
        assert response.status_code == 200

        data = response.json()
        assert data["user"]["name"] == "Updated Name"

    def test_delete_user(self, api_client, test_user_data):
        """Delete user."""
        create_resp = api_client.post("/api/users", json=test_user_data)
        if create_resp.status_code != 201:
            pytest.skip("Cannot create user")

        user_id = create_resp.json()["user"]["id"]

        del_resp = api_client.delete(f"/api/users/{user_id}")
        assert del_resp.status_code == 200

        get_resp = api_client.get(f"/api/users/{user_id}")
        assert get_resp.status_code == 404

    def test_list_users(self, api_client):
        """List all users."""
        response = api_client.get("/api/users")
        assert response.status_code == 200

        data = response.json()
        assert "users" in data


class TestOrders:
    """Order tests."""

    def test_create_order(self, api_client, created_user):
        """Create order for user."""
        if not created_user:
            pytest.skip("User not created")

        order_data = {"user_id": created_user, "amount": 1000.00}

        response = api_client.post("/api/orders", json=order_data)
        assert response.status_code == 201

        data = response.json()
        assert "order" in data
        assert data["order"]["amount"] == 1000

    def test_list_orders(self, api_client):
        """List orders."""
        response = api_client.get("/api/orders")
        assert response.status_code == 200

        data = response.json()
        assert "orders" in data
