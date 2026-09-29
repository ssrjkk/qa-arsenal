"""Locust load tests."""

from locust import HttpUser, task, between, events
import random


class UserScenario(HttpUser):
    """User scenario: register → view profile."""

    wait_time = between(1, 3)
    user_id = None

    def on_start(self):
        """Register user."""
        unique = random.randint(10000, 99999)
        response = self.client.post(
            "/api/users", json={"name": f"Load User {unique}", "email": f"load{unique}@test.com"}
        )

        if response.status_code == 201:
            self.user_id = response.json()["user"]["id"]

    @task(3)
    def view_users(self):
        """View users list."""
        self.client.get("/api/users")

    @task(2)
    def view_profile(self):
        """View user profile."""
        if self.user_id:
            self.client.get(f"/api/users/{self.user_id}")

    @task(1)
    def health_check(self):
        """Check health."""
        self.client.get("/health")


class ApiStressTest(HttpUser):
    """API stress test."""

    wait_time = between(0.1, 0.5)

    @task(10)
    def get_users(self):
        """GET /api/users"""
        self.client.get("/api/users")

    @task(5)
    def get_health(self):
        """GET /health"""
        self.client.get("/health")

    @task(3)
    def get_orders(self):
        """GET /api/orders"""
        self.client.get("/api/orders")

    @task(1)
    def create_user(self):
        """POST /api/users"""
        unique = random.randint(10000, 99999)
        self.client.post("/api/users", json={"name": f"Stress User {unique}", "email": f"stress{unique}@test.com"})


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """On test start."""
    print(f"Load test starting: {environment.runner.target_user_count} users")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """On test stop."""
    stats = environment.runner.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Fail ratio: {stats.total.fail_ratio:.2%}")
    print(f"Avg response time: {stats.total.avg_response_time:.2f}ms")
