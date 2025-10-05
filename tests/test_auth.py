def test_login_success(client, user):
    r = client.post("/login",
                    data={"email": "alice@example.com", "password": "password123"},
                    follow_redirects=True)
    assert r.status_code == 200
    # allow for slightly different flash wording
    assert b"Welcome" in r.data or b"logged in" in r.data.lower()

def test_login_fail(client, user):
    r = client.post("/login",
                    data={"email": "alice@example.com", "password": "wrong"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b"Login Unsuccessful" in r.data or b"unsuccessful" in r.data

def test_logout(login):
    r = login.get("/logout", follow_redirects=True)
    assert r.status_code == 200
    assert b"Logged out" in r.data or b"logout" in r.data.lower()
