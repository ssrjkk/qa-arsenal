package unit

import (
	"errors"
	"net/http"
	"strings"
	"testing"

	"go-framework-guap/core/errors"
)

func TestNewAPIError(t *testing.T) {
	e := errors.NewAPIError(500, "boom", "https://x")
	if e.StatusCode != 500 || e.Message != "boom" || e.URL != "https://x" {
		t.Fatalf("unexpected error: %+v", e)
	}
	if !strings.Contains(e.Error(), "500") {
		t.Fatalf("error string should contain status: %s", e.Error())
	}
}

func TestHandleHTTPError(t *testing.T) {
	if err := errors.HandleHTTPError(&http.Response{StatusCode: 200}, "u"); err != nil {
		t.Fatalf("2xx should not error: %v", err)
	}
	if err := errors.HandleHTTPError(&http.Response{StatusCode: 404}, "u"); err == nil {
		t.Fatal("4xx should error")
	}
	if err := errors.HandleHTTPError(&http.Response{StatusCode: 500}, "u"); err == nil {
		t.Fatal("5xx should error")
	}
}

func TestValidationError(t *testing.T) {
	e := errors.NewValidationError("email", "must be valid")
	if e.Field != "email" {
		t.Fatalf("unexpected field: %s", e.Field)
	}
	if !strings.Contains(e.Error(), "email") {
		t.Fatalf("error string should mention field: %s", e.Error())
	}
}

func TestErrorsImplementError(t *testing.T) {
	var err error = errors.NewAPIError(500, "x", "u")
	var err2 error = errors.NewValidationError("f", "m")
	if err == nil || err2 == nil {
		t.Fatal("should be non-nil errors")
	}
	if !errors.Is(err, err) {
		t.Fatal("should satisfy errors.Is with itself")
	}
}