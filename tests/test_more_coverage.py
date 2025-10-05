# tests/test_more_coverage.py
from app import db, Post, User

def test_home_and_about_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/about").status_code == 200

def test_register_flow(client):
    r = client.post("/register", data={
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "pw12345",
        "confirm_password": "pw12345",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Welcome" in r.data or b"account is ready" in r.data.lower()

def test_new_post_get_form(login):
    r = login.get("/post/new")
    assert r.status_code == 200
    assert b"New Post" in r.data

def test_post_detail_page(login):
    login.post("/post/new", data={"title": "Detail Me", "flair": "OTHER", "content": "content"}, follow_redirects=True)
    p = Post.query.order_by(Post.id.desc()).first()
    r = login.get(f"/post/{p.id}")
    assert r.status_code == 200
    assert b"Detail Me" in r.data

def test_edit_get_form_for_author(login):
    login.post("/post/new", data={"title": "Edit Me", "flair": "OTHER", "content": "x"}, follow_redirects=True)
    p = Post.query.order_by(Post.id.desc()).first()
    r = login.get(f"/post/{p.id}/edit")
    assert r.status_code == 200
    assert b"Edit Post" in r.data

def test_home_flair_filter(client, sample_post):
    assert client.get("/home?flair=OTHER").status_code == 200
    # also exercise branch where no posts for a flair
    assert client.get("/home?flair=WAIVER_WIRE").status_code == 200

def test_login_next_redirect(client, user):
    # Hit a protected route to get ?next= param
    r = client.get("/post/new", follow_redirects=False)
    assert r.status_code in (302, 401)
    login_url = r.headers.get("Location", "")
    assert "/login" in login_url and "next=%2Fpost%2Fnew" in login_url
    # Now log in with the next param; you should land on /post/new
    r = client.post("/login?next=%2Fpost%2Fnew",
                    data={"email": "alice@example.com", "password": "password123"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b"New Post" in r.data

def test_api_demo_page(client):
    r = client.get("/api-demo")
    assert r.status_code == 200
    assert b"API Demo" in r.data

def test_api_posts_search_and_pagination(login):
    u = User.query.first()
    for i in range(3):
        db.session.add(Post(title=f"P{i} rb sleepers", flair="OTHER", content="rb notes", author=u))
    db.session.commit()

    # invalid params exercise the ValueError branches
    r = login.get("/api/posts?page=abc&per_page=xyz&q=rb")
    assert r.status_code == 200 and r.is_json

    # pagination across pages
    r1 = login.get("/api/posts?per_page=1&q=rb&page=1")
    r2 = login.get("/api/posts?per_page=1&q=rb&page=2")
    d1, d2 = r1.get_json(), r2.get_json()
    assert d1["page"] == 1 and d2["page"] == 2
    assert len(d1["items"]) == 1 and len(d2["items"]) == 1

def test_api_stats(client, sample_post):
    r = client.get("/api/stats")
    assert r.status_code == 200 and r.is_json
    data = r.get_json()
    assert "counts" in data and "latest" in data

def test_comment_invalid_shows_flash(login, sample_post):
    # Empty content -> Form invalid -> else branch in add_comment
    r = login.post(f"/post/{sample_post.id}/comment", data={"content": ""}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Could not add comment" in r.data

def test_delete_forbidden_for_non_author(client, user, other_user):
    p = Post(title="Nope", flair="OTHER", content="x", author=user)
    db.session.add(p); db.session.commit()
    # login as other_user
    client.post("/login", data={"email": "bob@example.com", "password": "password123"}, follow_redirects=True)
    r = client.post(f"/post/{p.id}/delete", follow_redirects=False)
    assert r.status_code == 403
