from app import db, Post, User

def test_home_no_posts_message(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"No posts yet" in r.data or b"No posts" in r.data

def test_home_flair_no_results_message(client):
    r = client.get("/home?flair=WAIVER_WIRE")
    assert r.status_code == 200  # page still renders even if none

def test_post_detail_404(client):
    r = client.get("/post/999999")
    assert r.status_code == 404

def test_edit_post_forbidden_post(login, other_user):
    # create a post by someone else
    p = Post(title="Foreign", flair="OTHER", content="x", author=other_user)
    db.session.add(p); db.session.commit()
    # author != current_user -> 403 on GET and POST
    r = login.get(f"/post/{p.id}/edit")
    assert r.status_code == 403
    r = login.post(f"/post/{p.id}/edit", data={"title":"x","flair":"OTHER","content":"y"})
    assert r.status_code == 403

def test_delete_post_404(login):
    r = login.post("/post/999999/delete")
    assert r.status_code == 404

def test_create_post_invalid_missing_title(login):
    before = Post.query.count()
    r = login.post("/post/new", data={"title":"", "flair":"OTHER", "content":"hello"})
    # validation fails, stays on page
    assert r.status_code == 200
    assert Post.query.count() == before

def test_edit_post_invalid_no_change(login):
    # create
    r = login.post("/post/new", data={"title":"T", "flair":"OTHER", "content":"C"}, follow_redirects=True)
    assert r.status_code == 200
    p = Post.query.order_by(Post.id.desc()).first()
    # invalid update (empty title) should not change DB
    r = login.post(f"/post/{p.id}/edit", data={"title":"", "flair":"OTHER", "content":"C"}, follow_redirects=True)
    assert r.status_code == 200
    assert Post.query.get(p.id).title == "T"
