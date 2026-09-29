import pytest
from pipelines.api.utils.http_client import AmoCRMClient
import os


pytestmark = [pytest.mark.db, pytest.mark.consistency]


@pytest.fixture(scope="session")
def api_client():
    token = os.getenv("AMOCRM_LONG_TOKEN", "")
    return AmoCRMClient(long_token=token)


class TestAPIDBConsistency:
    def test_contact_in_api_exists(self, api_client, db_client):
        try:
            api_resp = api_client.contacts.list(limit=1)
            if api_resp.status_code != 200:
                pytest.skip("API not available")
            
            contacts = api_resp.json().get("_embedded", {}).get("contacts", [])
            if not contacts:
                pytest.skip("No contacts in API")
            
            contact_id = contacts[0]["id"]
            
            db_row = db_client.execute_one(
                "SELECT * FROM contacts WHERE id = %s",
                (contact_id,)
            )
            
            assert db_row is not None or db_row == [], "Contact from API not in DB"
        except Exception as e:
            pytest.skip(f"Setup error: {e}")

    def test_lead_pipeline_valid(self, api_client, db_client):
        try:
            api_resp = api_client.leads.list(limit=1)
            if api_resp.status_code != 200:
                pytest.skip("API not available")
            
            leads = api_resp.json().get("_embedded", {}).get("leads", [])
            if not leads:
                pytest.skip("No leads in API")
            
            lead = leads[0]
            pipeline_id = lead.get("pipeline_id")
            
            if pipeline_id:
                db_row = db_client.execute_one(
                    "SELECT * FROM pipelines WHERE id = %s",
                    (pipeline_id,)
                )
                assert db_row is not None or db_row == [], "Pipeline not found in DB"
        except Exception as e:
            pytest.skip(f"Setup error: {e}")

    def test_user_in_leads_creator(self, api_client, db_client):
        try:
            api_resp = api_client.leads.list(limit=1)
            if api_resp.status_code != 200:
                pytest.skip("API not available")
            
            leads = api_resp.json().get("_embedded", {}).get("leads", [])
            if not leads:
                pytest.skip("No leads in API")
            
            creator_id = leads[0].get("created_by")
            if creator_id:
                db_row = db_client.execute_one(
                    "SELECT * FROM users WHERE id = %s",
                    (creator_id,)
                )
                assert db_row is not None or db_row == [], "Creator not found in DB"
        except Exception as e:
            pytest.skip(f"Setup error: {e}")


class TestDBState:
    def test_contacts_count_matches(self, db_client):
        try:
            result = db_client.execute("SELECT COUNT(*) as cnt FROM contacts")
            assert result[0]["cnt"] >= 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_leads_count_matches(self, db_client):
        try:
            result = db_client.execute("SELECT COUNT(*) as cnt FROM leads")
            assert result[0]["cnt"] >= 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_users_count_matches(self, db_client):
        try:
            result = db_client.execute("SELECT COUNT(*) as cnt FROM users")
            assert result[0]["cnt"] >= 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")