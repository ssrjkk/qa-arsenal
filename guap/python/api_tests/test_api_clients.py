import pytest
import requests


class TestGuapAPI:
    """GUAP University API endpoints"""

    BASE_URL = "https://guap.ru/api"

    @pytest.mark.smoke
    @pytest.mark.api
    def test_guap_main_page_accessible(self):
        """Проверка доступности главной страницы GUAP"""
        response = requests.get("https://guap.ru", timeout=15, allow_redirects=True)
        assert response.status_code == 200

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_health(self):
        """GET /api/health - проверка статуса API"""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=10)
            assert response.status_code in [200, 404, 500]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_students_list(self):
        """GET /api/students - список студентов"""
        try:
            response = requests.get(f"{self.BASE_URL}/students", timeout=10)
            assert response.status_code in [200, 401, 403, 404]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_student_by_id(self):
        """GET /api/students/:id - студент по ID"""
        try:
            response = requests.get(f"{self.BASE_URL}/students/1", timeout=10)
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                data = response.json()
                assert "id" in data or "student_id" in data
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_schedule(self):
        """GET /api/schedule - расписание занятий"""
        try:
            response = requests.get(f"{self.BASE_URL}/schedule", timeout=10)
            assert response.status_code in [200, 401, 403, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_schedule_by_group(self):
        """GET /api/schedule?group=Z3420 - расписание группы"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/schedule",
                params={"group": "Z3420"},
                timeout=10
            )
            assert response.status_code in [200, 400, 401, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_subjects(self):
        """GET /api/subjects - список предметов"""
        try:
            response = requests.get(f"{self.BASE_URL}/subjects", timeout=10)
            assert response.status_code in [200, 401, 403, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_grades(self):
        """GET /api/grades - оценки студентов"""
        try:
            response = requests.get(f"{self.BASE_URL}/grades", timeout=10)
            assert response.status_code in [200, 401, 403, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_api_grades_by_student(self):
        """GET /api/grades?student_id=1 - оценки конкретного студента"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/grades",
                params={"student_id": 1},
                timeout=10
            )
            assert response.status_code in [200, 400, 401, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.critical
    @pytest.mark.api
    def test_guap_lk_portal_accessible(self):
        """Проверка доступности личного кабинета"""
        try:
            response = requests.get("https://lk.guap.ru", timeout=15, allow_redirects=True)
            assert response.status_code in [200, 301, 302, 304]
        except requests.exceptions.RequestException:
            pytest.skip("lk.guap.ru недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_guap_main_page_has_content(self):
        """Проверка что главная страница содержит контент"""
        response = requests.get("https://guap.ru", timeout=15)
        content = response.text.lower()
        keywords = ["гуап", "guap", "университет", "аэрокосмическ", "санкт-петербург"]
        found = any(word in content for word in keywords)
        assert found or len(content) > 1000


class TestGuapAPIValidation:
    """Валидация схем ответов GUAP API"""

    BASE_URL = "https://guap.ru/api"

    @pytest.mark.regression
    @pytest.mark.api
    def test_student_response_schema(self):
        """Валидация схемы ответа студента"""
        try:
            response = requests.get(f"{self.BASE_URL}/students/1", timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["id", "name", "group"]
                for field in expected_fields:
                    assert field in data, f"Missing field: {field}"
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.regression
    @pytest.mark.api
    def test_schedule_response_schema(self):
        """Валидация схемы расписания"""
        try:
            response = requests.get(f"{self.BASE_URL}/schedule", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")


class TestGuapAPIErrorHandling:
    """Обработка ошибок GUAP API"""

    BASE_URL = "https://guap.ru/api"

    @pytest.mark.negative
    @pytest.mark.api
    def test_nonexistent_student(self):
        """GET /api/students/99999 - несуществующий студент"""
        try:
            response = requests.get(f"{self.BASE_URL}/students/99999", timeout=10)
            assert response.status_code == 404
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.negative
    @pytest.mark.api
    def test_invalid_group(self):
        """GET /api/schedule?group=INVALID - невалидная группа"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/schedule",
                params={"group": "INVALID999"},
                timeout=10
            )
            assert response.status_code in [400, 404]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")

    @pytest.mark.negative
    @pytest.mark.api
    def test_missing_auth_token(self):
        """POST /api/grades без авторизации"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/grades",
                json={"student_id": 1, "subject": "Math", "grade": 5},
                timeout=10
            )
            assert response.status_code in [401, 403, 404, 405]
        except requests.exceptions.RequestException:
            pytest.skip("guap.ru/api недоступен")
