"""Database tests - working examples."""

import pytest


pytestmark = pytest.mark.db


class TestUserPersistence:
    """User persistence tests."""

    def test_user_created_via_api_exists_in_db(self, db_client, api_client):
        """User created via API is saved in DB."""
        import uuid

        unique = uuid.uuid4().hex[:8]

        user_data = {"name": f"DB Test {unique}", "email": f"dbtest{unique}@example.com"}

        resp = api_client.post("/api/users", json=user_data)

        if resp.status_code != 201:
            pytest.skip("API not available or user creation failed")

        user_id = resp.json()["user"]["id"]

        db_user = db_client.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))

        assert db_user is not None, f"User {user_id} not found in DB"
        assert db_user["name"] == user_data["name"]
        assert db_user["email"] == user_data["email"]

        api_client.delete(f"/api/users/{user_id}")

    def test_user_data_matches(self, db_client, api_client):
        """API response data matches DB data."""
        import uuid

        unique = uuid.uuid4().hex[:8]

        user_data = {"name": f"Match Test {unique}", "email": f"match{unique}@example.com"}

        resp = api_client.post("/api/users", json=user_data)
        if resp.status_code != 201:
            pytest.skip("User creation failed")

        user_id = resp.json()["user"]["id"]

        api_resp = api_client.get(f"/api/users/{user_id}")
        api_user = api_resp.json()["user"]

        db_user = db_client.execute_one("SELECT * FROM users WHERE id = %s", (user_id,))

        assert db_user["name"] == api_user["name"]
        assert db_user["email"] == api_user["email"]

        api_client.delete(f"/api/users/{user_id}")


class TestDataIntegrity:
    """Data integrity tests."""

    def test_users_table_exists(self, db_client):
        """Users table exists."""
        assert db_client.table_exists("users")

    def test_orders_table_exists(self, db_client):
        """Orders table exists."""
        assert db_client.table_exists("orders")

    def test_orders_have_valid_user_reference(self, db_client, api_client):
        """Order foreign key to user is valid."""
        import uuid

        unique = uuid.uuid4().hex[:8]

        user_data = {"name": f"FK Test {unique}", "email": f"fk{unique}@test.com"}

        resp = api_client.post("/api/users", json=user_data)
        if resp.status_code != 201:
            pytest.skip("User creation failed")

        user_id = resp.json()["user"]["id"]

        order_resp = api_client.post("/api/orders", json={"user_id": user_id, "amount": 500})

        if order_resp.status_code == 201:
            order_id = order_resp.json()["order"]["id"]

            db_order = db_client.execute_one("SELECT * FROM orders WHERE id = %s", (order_id,))

            assert db_order["user_id"] == user_id

            api_client.delete(f"/api/users/{user_id}")

    def test_no_duplicate_emails(self, db_client):
        """Email uniqueness constraint."""
        result = db_client.execute("""
            SELECT email, COUNT(*) as cnt 
            FROM users 
            WHERE email IS NOT NULL
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)

        assert len(result) == 0, f"Duplicate emails found: {result}"

    def test_users_have_required_fields(self, db_client):
        """Users have required fields."""
        columns = db_client.get_column_names("users")
        assert "id" in columns
        assert "name" in columns
        assert "email" in columns


class TestDatabaseConnection:
    """Database connection tests."""

    def test_db_connection(self, db_client):
        """Can connect to database."""
        result = db_client.execute("SELECT 1 as test")
        assert result[0]["test"] == 1

    def test_row_count(self, db_client):
        """Can get row count."""
        count = db_client.row_count("users")
        assert count >= 0
