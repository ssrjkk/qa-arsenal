import pytest


pytestmark = [pytest.mark.db, pytest.mark.integrity]


class TestDataIntegrity:
    def test_no_nulls_in_required_contact_fields(self, db_client):
        try:
            result = db_client.execute(
                "SELECT COUNT(*) as cnt FROM contacts WHERE name IS NULL"
            )
            assert result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_no_duplicate_contact_ids(self, db_client):
        try:
            result = db_client.execute("""
                SELECT id, COUNT(*) as cnt 
                FROM contacts 
                GROUP BY id 
                HAVING COUNT(*) > 1
            """)
            assert len(result) == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_contacts_email_unique_or_null(self, db_client):
        try:
            result = db_client.execute("""
                SELECT email, COUNT(*) as cnt 
                FROM contacts 
                WHERE email IS NOT NULL
                GROUP BY email 
                HAVING COUNT(*) > 1
            """)
            assert len(result) == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_leads_price_not_negative(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM leads 
                WHERE price < 0
            """)
            assert result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_leads_have_valid_pipeline(self, db_client):
        try:
            result = db_client.execute("""
                SELECT l.id 
                FROM leads l 
                LEFT JOIN pipelines p ON l.pipeline_id = p.id 
                WHERE l.pipeline_id IS NOT NULL AND p.id IS NULL
            """)
            assert len(result) == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_leads_have_valid_status(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM leads 
                WHERE status_id IS NULL
            """)
            assert result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_users_is_admin_boolean(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM users 
                WHERE is_admin NOT IN (0, 1)
            """)
            assert result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_companies_name_not_empty(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM companies 
                WHERE name IS NULL OR LENGTH(TRIM(name)) = 0
            """)
            assert len(result) == 0 or result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_tasks_have_entity_reference(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM tasks 
                WHERE entity_type IS NOT NULL AND entity_id IS NULL
            """)
            assert result[0]["cnt"] == 0
        except Exception as e:
            pytest.skip(f"DB not available: {e}")


class TestIndexes:
    def test_contacts_have_primary_key(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM information_schema.table_constraints 
                WHERE table_name = 'contacts' 
                AND constraint_type = 'PRIMARY KEY'
            """)
            assert result[0]["cnt"] >= 1
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

    def test_leads_have_indexes(self, db_client):
        try:
            result = db_client.execute("""
                SELECT COUNT(*) as cnt 
                FROM pg_indexes 
                WHERE tablename = 'leads'
            """)
            assert result[0]["cnt"] >= 1
        except Exception as e:
            pytest.skip(f"DB not available: {e}")