package unit

import (
	"testing"

	"go-framework-guap/core/base"
)

type User struct {
	Name  string
	Email string
	Age   int
}

func TestRequired(t *testing.T) {
	if err := base.Required("name", ""); err == nil {
		t.Fatal("empty string should be rejected")
	}
	if err := base.Required("name", "alice"); err != nil {
		t.Fatalf("non-empty should pass: %v", err)
	}
}

func TestMinLength(t *testing.T) {
	rule := base.MinLength(3)
	if err := rule("name", "ab"); err == nil {
		t.Fatal("short string should fail")
	}
	if err := rule("name", "abcd"); err != nil {
		t.Fatalf("long enough string should pass: %v", err)
	}
}

func TestEmail(t *testing.T) {
	if err := base.Email("email", "bad-email"); err == nil {
		t.Fatal("invalid email should fail")
	}
	if err := base.Email("email", "a@b.com"); err != nil {
		t.Fatalf("valid email should pass: %v", err)
	}
	// Empty email passes (optional).
	if err := base.Email("email", ""); err != nil {
		t.Fatal("empty email should pass")
	}
}

func TestRange(t *testing.T) {
	rule := base.Range(18, 99)
	if err := rule("age", 17); err == nil {
		t.Fatal("below min should fail")
	}
	if err := rule("age", 100); err == nil {
		t.Fatal("above max should fail")
	}
	if err := rule("age", 30); err != nil {
		t.Fatalf("in range should pass: %v", err)
	}
}

func TestValidatorOnStruct(t *testing.T) {
	v := base.NewValidator()
	v.AddRule("Name", base.Required)
	v.AddRule("Email", base.Email)

	ok := User{Name: "alice", Email: "alice@example.com"}
	if errs := v.Validate(ok); len(errs) != 0 {
		t.Fatalf("valid struct should pass, got %v", errs)
	}

	bad := User{Name: "", Email: "nope"}
	if errs := v.Validate(bad); len(errs) != 2 {
		t.Fatalf("expected 2 errors, got %v", errs)
	}
}

func TestSchemaValidation(t *testing.T) {
	s := base.NewSchema()
	s.Field("Name").Required().MinLength(3)
	s.Field("Email").Email()

	ok := User{Name: "alice", Email: "a@b.com"}
	if errs := s.Validate(ok); len(errs) != 0 {
		t.Fatalf("valid struct should pass, got %v", errs)
	}

	bad := User{Name: "x", Email: "bad"}
	if errs := s.Validate(bad); len(errs) == 0 {
		t.Fatal("expected errors for invalid struct")
	}
}

func TestValidateJSONSchema(t *testing.T) {
	schema := base.JSONSchema{
		"required":   []string{"id", "name"},
		"properties": map[string]interface{}{"name": map[string]interface{}{"type": "string", "minLength": float64(3)}},
	}

	if errs := base.ValidateJSONSchema(map[string]interface{}{"id": 1}, schema); len(errs) != 1 {
		t.Fatalf("expected 1 required error, got %v", errs)
	}

	if errs := base.ValidateJSONSchema(map[string]interface{}{"id": 1, "name": "ab"}, schema); len(errs) != 0 {
		t.Fatalf("short name should produce an error, got %v", errs)
	}

	if errs := base.ValidateJSONSchema(map[string]interface{}{"id": 1, "name": "alice"}, schema); len(errs) != 0 {
		t.Fatalf("valid object should pass, got %v", errs)
	}
}