from app import db, Post, User

def test_add_comment_requires_login_redirect(client, sample_post):
    r = client.post(f"/post/{sample_post.id}/comment", data={"content":"hi"}, follow_redirects=False)
    assert r.status_code in (302, 401)
    assert "/login" in r.headers.get("Location", "")

def test_comment_on_nonexistent_post_404(login):
    r = login.post("/post/999999/comment", data={"content":"x"})
    assert r.status_code == 404

def test_comments_api_sorted_ascending(login, user):
    p = Post(title="Sort", flair="OTHER", content="x", author=user)
    db.session.add(p); db.session.commit()
    # add two comments in order
    login.post(f"/post/{p.id}/comment", data={"content":"first"}, follow_redirects=True)
    login.post(f"/post/{p.id}/comment", data={"content":"second"}, follow_redirects=True)
    r = login.get(f"/api/posts/{p.id}/comments")
    data = r.get_json()
    items = data["items"]
    assert len(items) == 2
    assert items[0]["content"] == "first"
    assert items[1]["content"] == "second"

def test_seed_idempotent(client):
    r1 = client.get("/seed", follow_redirects=True)
    assert r1.status_code == 200
    r2 = client.get("/seed", follow_redirects=True)  # second call should not error
    assert r2.status_code == 200
