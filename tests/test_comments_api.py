def test_add_comment_and_list(login, sample_post):
    # add a comment (auth required)
    r = login.post(f"/post/{sample_post.id}/comment",
                   data={"content": "nice!"},
                   follow_redirects=True)
    assert r.status_code == 200
    assert b"Comment added" in r.data

    # list via API
    r = login.get(f"/api/posts/{sample_post.id}/comments")
    assert r.is_json
    data = r.get_json()
    assert data["total"] == 1
    assert data["items"][0]["content"] == "nice!"

def test_api_list_filter_detail(client, sample_post):
    # list
    r = client.get("/api/posts")
    assert r.status_code == 200 and r.is_json
    assert len(r.get_json()["items"]) >= 1

    # filter by flair
    r = client.get("/api/posts?flair=OTHER")
    assert r.status_code == 200 and r.is_json
    assert len(r.get_json()["items"]) >= 1

    # detail
    r = client.get(f"/api/posts/{sample_post.id}")
    assert r.status_code == 200 and r.is_json
    assert r.get_json()["title"] == sample_post.title

def test_health_and_export(client, sample_post):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}

    r = client.get("/api/export/posts")
    assert r.status_code == 200
    cd = r.headers.get("Content-Disposition", "").lower()
    assert "attachment" in cd and cd.endswith('.json"') or cd.endswith(".json'")
