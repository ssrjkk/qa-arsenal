package unit

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"go-framework-guap/core/base"
)

func newFastClient(baseURL string) *base.Client {
	return base.NewClient(base.Config{
		BaseURL:    baseURL,
		Timeout:    2 * time.Second,
		MaxRetries: 1,
		RetryDelay: time.Millisecond,
	})
}

func TestClientGetAndDecode(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"name":"alice","age":30}`))
	}))
	defer srv.Close()

	client := newFastClient(srv.URL)
	resp, err := client.Get(context.Background(), "/users/1", nil)
	if err != nil {
		t.Fatalf("GET failed: %v", err)
	}
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}

	var user struct {
		Name string `json:"name"`
		Age  int    `json:"age"`
	}
	if err := client.DecodeJSON(resp, &user); err != nil {
		t.Fatalf("decode failed: %v", err)
	}
	if user.Name != "alice" || user.Age != 30 {
		t.Fatalf("unexpected payload: %+v", user)
	}
}

func TestClientPostSendsJSONBody(t *testing.T) {
	var gotBody map[string]interface{}
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if ct := r.Header.Get("Content-Type"); !strings.Contains(ct, "application/json") {
			t.Errorf("expected json content type, got %q", ct)
		}
		_ = json.NewDecoder(r.Body).Decode(&gotBody)
		w.WriteHeader(201)
	}))
	defer srv.Close()

	client := newFastClient(srv.URL)
	resp, err := client.Post(context.Background(), "/items", map[string]interface{}{"title": "x"})
	if err != nil {
		t.Fatalf("POST failed: %v", err)
	}
	if resp.StatusCode != 201 {
		t.Fatalf("expected 201, got %d", resp.StatusCode)
	}
	if gotBody["title"] != "x" {
		t.Fatalf("unexpected body: %v", gotBody)
	}
}

func TestClientRetriesOnServerError(t *testing.T) {
	attempts := 0
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		attempts++
		if attempts == 1 {
			w.WriteHeader(500)
			return
		}
		w.WriteHeader(200)
	}))
	defer srv.Close()

	client := newFastClient(srv.URL)
	resp, err := client.Get(context.Background(), "/flaky", nil)
	if err != nil {
		t.Fatalf("GET failed: %v", err)
	}
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200 after retry, got %d", resp.StatusCode)
	}
	if attempts != 2 {
		t.Fatalf("expected 2 attempts (initial + 1 retry), got %d", attempts)
	}
}

func TestClientSendsQueryParams(t *testing.T) {
	var gotQuery map[string][]string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotQuery = r.URL.Query()
		w.WriteHeader(200)
	}))
	defer srv.Close()

	client := newFastClient(srv.URL)
	if _, err := client.Get(context.Background(), "/users", map[string]string{"page": "2", "active": "true"}); err != nil {
		t.Fatalf("GET failed: %v", err)
	}
	if gotQuery["page"][0] != "2" || gotQuery["active"][0] != "true" {
		t.Fatalf("query params not forwarded: %v", gotQuery)
	}
}

func TestValidateEmail(t *testing.T) {
	if !base.ValidateEmail("a@b.com") {
		t.Fatal("valid email rejected")
	}
	if base.ValidateEmail("not-an-email") {
		t.Fatal("invalid email accepted")
	}
}

func TestValidateRequired(t *testing.T) {
	if err := base.ValidateRequired("", "name"); err == nil {
		t.Fatal("empty should fail")
	}
	if err := base.ValidateRequired("  ", "name"); err == nil {
		t.Fatal("whitespace should fail")
	}
	if err := base.ValidateRequired("alice", "name"); err != nil {
		t.Fatalf("non-empty should pass: %v", err)
	}
}

func TestValidateRange(t *testing.T) {
	if err := base.ValidateRange("ab", "name", 3, 10); err == nil {
		t.Fatal("too short should fail")
	}
	if err := base.ValidateRange("abcdefghijkl", "name", 3, 10); err == nil {
		t.Fatal("too long should fail")
	}
	if err := base.ValidateRange("abcde", "name", 3, 10); err != nil {
		t.Fatalf("in range should pass: %v", err)
	}
}