"""API tests for https://reqres.in (requests + pytest).

reqres.in now requires a free API key on every request. Create one at
https://app.reqres.in and export it:  REQRES_API_KEY=<your key>
Tests are skipped (with a clear reason) if the key is missing.
"""
import os

import pytest
import requests

pytestmark = pytest.mark.api

BASE = "https://reqres.in/api"
API_KEY = os.getenv("REQRES_API_KEY")
HEADERS = {
    "x-api-key": API_KEY or "",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "qa-assignment-tests/1.0",
}
needs_key = pytest.mark.skipif(not API_KEY, reason="Set REQRES_API_KEY (free key from https://app.reqres.in)")

USER_FIELDS = {"id": int, "email": str, "first_name": str, "last_name": str, "avatar": str}


def call(method, path, **kw):
    return requests.request(method, BASE + path, headers=HEADERS, timeout=30, **kw)


def assert_user_shape(user):
    for field, typ in USER_FIELDS.items():
        assert field in user, f"missing '{field}' in {user}"
        assert isinstance(user[field], typ), f"'{field}' should be {typ.__name__}"


# ------------------------------------------------------------------ GET
@needs_key
def test_get_users_list_success():
    r = call("GET", "/users", params={"page": 2})
    assert r.status_code == 200
    assert "application/json" in r.headers["Content-Type"]
    body = r.json()
    for key in ("page", "per_page", "total", "total_pages", "data"):
        assert key in body, f"missing '{key}'"
    assert body["page"] == 2
    assert isinstance(body["data"], list) and 0 < len(body["data"]) <= body["per_page"]
    for user in body["data"]:
        assert_user_shape(user)


@needs_key
def test_get_single_user_success():
    r = call("GET", "/users/2")
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["id"] == 2
    assert_user_shape(body["data"])


@needs_key
def test_get_user_not_found_returns_404():
    r = call("GET", "/users/23")
    assert r.status_code == 404
    assert r.json() == {}


@needs_key
def test_get_unknown_resource_returns_404():
    r = call("GET", "/unknown/23")
    assert r.status_code == 404


# ------------------------------------------------------------------ POST
@needs_key
def test_create_user_success():
    payload = {"name": "morpheus", "job": "leader"}
    r = call("POST", "/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == payload["name"]
    assert body["job"] == payload["job"]
    assert isinstance(body["id"], (str, int)) and str(body["id"])
    assert isinstance(body["createdAt"], str) and body["createdAt"].endswith("Z")


@needs_key
def test_login_success_returns_token():
    r = call("POST", "/login", json={"email": "eve.holt@reqres.in", "password": "cityslicka"})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"token"}
    assert isinstance(body["token"], str) and body["token"]


@needs_key
def test_register_success_returns_id_and_token():
    r = call("POST", "/register", json={"email": "eve.holt@reqres.in", "password": "pistol"})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["id"], int)
    assert isinstance(body["token"], str) and body["token"]


# ------------------------------------------------------------------ invalid / missing data
@needs_key
def test_login_missing_password_returns_400():
    r = call("POST", "/login", json={"email": "peter@klaven"})
    assert r.status_code == 400
    assert r.json() == {"error": "Missing password"}


@needs_key
def test_login_missing_email_returns_400():
    r = call("POST", "/login", json={"password": "cityslicka"})
    assert r.status_code == 400
    assert r.json() == {"error": "Missing email or username"}


@needs_key
def test_register_missing_password_returns_400():
    r = call("POST", "/register", json={"email": "sydney@fife"})
    assert r.status_code == 400
    assert r.json() == {"error": "Missing password"}


@needs_key
def test_register_undefined_user_rejected():
    r = call("POST", "/register", json={"email": "not.a.user@example.com", "password": "pw"})
    assert r.status_code == 400
    assert "error" in r.json()


# ------------------------------------------------------------------ PUT / DELETE
@needs_key
def test_update_user_success():
    r = call("PUT", "/users/2", json={"name": "morpheus", "job": "zion resident"})
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "morpheus" and body["job"] == "zion resident"
    assert isinstance(body["updatedAt"], str)


@needs_key
def test_delete_user_returns_204_no_body():
    r = call("DELETE", "/users/2")
    assert r.status_code == 204
    assert r.text == ""


# ------------------------------------------------------------------ auth gate
def test_request_without_api_key_is_rejected():
    r = requests.get(BASE + "/users/2", headers={"User-Agent": "qa-assignment-tests/1.0"}, timeout=30)
    assert r.status_code in (401, 403)
