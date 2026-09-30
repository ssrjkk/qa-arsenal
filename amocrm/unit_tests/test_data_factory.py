"""Hermetic unit tests for the data factory (no network)."""

from fixtures.data_factory import DataFactory


class TestRandomStrings:
    def test_random_string_length(self):
        df = DataFactory()
        assert len(df.random_string(15)) == 15

    def test_random_string_respects_charset(self):
        df = DataFactory()
        value = df.random_string(20, chars="ab")
        assert set(value) <= {"a", "b"}

    def test_random_int_within_bounds(self):
        df = DataFactory()
        for _ in range(50):
            value = df.random_int(5, 10)
            assert 5 <= value <= 10

    def test_random_float_decimals(self):
        df = DataFactory()
        value = df.random_float(0.0, 10.0, decimals=2)
        assert round(value, 2) == value


class TestRandomContacts:
    def test_random_email_has_at(self):
        df = DataFactory()
        assert "@" in df.random_email()

    def test_random_phone_ru_format(self):
        df = DataFactory()
        phone = df.random_phone(format="ru")
        assert phone.startswith("+7")
        assert len(phone) == 12

    def test_random_name_non_empty(self):
        df = DataFactory()
        assert len(df.random_name()) > 0

    def test_random_company_non_empty(self):
        df = DataFactory()
        assert len(df.random_company()) > 0


class TestMisc:
    def test_random_url(self):
        df = DataFactory()
        assert df.random_url().startswith("http")

    def test_random_text_length(self):
        df = DataFactory()
        text = df.random_text(max_chars=30)
        assert len(text) <= 30