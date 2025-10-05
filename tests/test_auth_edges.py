from urllib.parse import quote

def test_register_duplicate_username_email(client, user):
    # duplicate username
    r = client.post("/register", data={
        "username": "alice",
        "email": "new@example.com",
        "password": "pw12345",
        "confirm_password": "pw12345",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Username or email already taken" in r.data

    # duplicate email
    r = client.post("/register", data={
        "username": "newname",
        "email": "alice@example.com",
        "password": "pw12345",
        "confirm_password": "pw12345",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Username or email already taken" in r.data

def test_register_invalid_email(client):
    r = client.post("/register", data={
        "username": "badmail",
        "email": "not-an-email",
        "password": "pw12345",
        "confirm_password": "pw12345",
    }, follow_redirects=True)
    # stays on page; no welcome flash
    assert r.status_code == 200
    assert b"Welcome" not in r.data

def test_register_password_mismatch(client):
    r = client.post("/register", data={
        "username": "mismatch",
        "email": "mismatch@example.com",
        "password": "pw12345",
        "confirm_password": "pw123456",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Welcome" not in r.data

def test_login_already_authenticated_redirects(client, user):
    # login once
    client.post("/login", data={"email": "alice@example.com", "password": "password123"}, follow_redirects=True)
    # visiting /login again should redirect to home
    r = client.get("/login", follow_redirects=False)
    assert r.status_code in (302, 301)
    assert "/home" in r.headers.get("Location", "") or "/" in r.headers.get("Location", "")

def test_register_when_authenticated_redirects(client, user):
    client.post("/login", data={"email": "alice@example.com", "password": "password123"}, follow_redirects=True)
    r = client.get("/register", follow_redirects=False)
    assert r.status_code in (302, 301)

def test_logout_requires_login_redirect(client):
    r = client.get("/logout", follow_redirects=False)
    assert r.status_code in (302, 401)
    # typically redirects to login
    assert "/login" in r.headers.get("Location", "")

def test_login_next_roundtrip(client, user):
    nxt = quote("/post/new")
    r = client.post(f"/login?next={nxt}",
                    data={"email": "alice@example.com", "password": "password123"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b"New Post" in r.data
