import json
from app import db, Post, User

def test_api_post_detail_404(client):
    r = client.get("/api/posts/999999")
    assert r.status_code == 404

def test_api_comments_404(client):
    r = client.get("/api/posts/999999/comments")
    assert r.status_code == 404

def test_api_posts_per_page_clamped_max(login):
    # create some posts
    u = User.query.first()
    for i in range(3):
        db.session.add(Post(title=f"Post {i}", flair="OTHER", content="x", author=u))
    db.session.commit()
    r = login.get("/api/posts?per_page=1000")
    data = r.get_json()
    assert r.status_code == 200
    assert data["per_page"] == 50  # clamped

def test_api_posts_per_page_min_and_page_min(login):
    r = login.get("/api/posts?per_page=0&page=0")
    data = r.get_json()
    assert r.status_code == 200
    assert data["per_page"] == 1
    assert data["page"] == 1

def test_api_filter_unknown_flair(client):
    r = client.get("/api/posts?flair=DOES_NOT_EXIST")
    data = r.get_json()
    assert r.status_code == 200
    assert isinstance(data["items"], list)

def test_api_search_case_insensitive(login):
    u = User.query.first()
    db.session.add(Post(title="RB Sleepers", flair="OTHER", content="UPPERCASE TEXT", author=u))
    db.session.commit()
    r = login.get("/api/posts?q=sleepers")
    assert r.status_code == 200
    titles = [it["title"].lower() for it in r.get_json()["items"]]
    assert any("sleepers" in t for t in titles)

def test_api_export_matches_count(login):
    total = Post.query.count()
    r = login.get("/api/export/posts")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("Content-Disposition", "").lower()
    data = json.loads(r.data.decode("utf-8"))
    assert isinstance(data, list)
    assert len(data) == total

def test_api_order_newest_first(login):
    u = User.query.first()
    db.session.add_all([
        Post(title="older", flair="OTHER", content="a", author=u),
        Post(title="newer", flair="OTHER", content="b", author=u),
    ])
    db.session.commit()
    r = login.get("/api/posts")
    items = r.get_json()["items"]
    # The last created ("newer") should appear before "older"
    titles = [it["title"] for it in items]
    assert titles.index("newer") < titles.index("older")
