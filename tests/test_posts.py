from app import Post

def test_new_post_requires_login(client):
    r = client.get("/post/new")
    # login_required should redirect to login
    assert r.status_code in (302, 401)
    if r.status_code == 302:
        assert "/login" in r.headers.get("Location", "")

def test_create_edit_delete_post_flow(login):
    # Create
    r = login.post("/post/new",
                   data={"title": "My Post", "flair": "OTHER", "content": "hello"},
                   follow_redirects=True)
    assert r.status_code == 200
    assert b"Post published" in r.data

    # Find post
    p = Post.query.order_by(Post.id.desc()).first()
    assert p and p.title == "My Post"

    # Edit
    r = login.post(f"/post/{p.id}/edit",
                   data={"title": "Edited", "flair": "OTHER", "content": "updated"},
                   follow_redirects=True)
    assert r.status_code == 200
    assert b"Post updated" in r.data or b"Edited" in r.data

    # Delete
    r = login.post(f"/post/{p.id}/delete", data={}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Post deleted" in r.data

def test_permission_enforced(client, user, other_user):
    # user creates a post
    from app import db, Post
    p = Post(title="Owner Only", flair="OTHER", content="secret", author=user)
    db.session.add(p); db.session.commit()

    # login as someone else
    r = client.post("/login",
                    data={"email": "bob@example.com", "password": "password123"},
                    follow_redirects=True)
    assert r.status_code == 200

    # edit should be forbidden
    r = client.get(f"/post/{p.id}/edit")
    assert r.status_code == 403
