def test_default_pagination_empty_db(client):
    response = client.get("/api/exchanges")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_default_pagination_with_data(client, seed_exchanges):
    response = client.get("/api/exchanges")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(seed_exchanges)
    assert len(data["items"]) == min(10, len(seed_exchanges))
    for item in data["items"]:
        assert "id" in item
        assert "book_title" in item
        assert "counterpart_nickname" in item
        assert "is_completed" in item


def test_keyword_match_book_title(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"keyword": "三体"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert "三体" in item["book_title"]


def test_keyword_match_book_title_partial(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"keyword": "活着"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    titles = {item["book_title"] for item in data["items"]}
    assert "活着" in titles
    assert "活着2续篇" in titles


def test_keyword_match_counterpart_nickname(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"keyword": "书友A"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["counterpart_nickname"] == "书友A"


def test_keyword_no_match(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"keyword": "不存在的书"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_status_completed(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["is_completed"] is True
    completed_count = sum(1 for e in seed_exchanges if e.is_completed)
    assert data["total"] == completed_count


def test_status_in_progress(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"status": "in_progress"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for item in data["items"]:
        assert item["is_completed"] is False
    in_progress_count = sum(1 for e in seed_exchanges if not e.is_completed)
    assert data["total"] == in_progress_count


def test_status_completed_exact_count(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"status": "completed"})
    assert response.json()["total"] == 6


def test_status_in_progress_exact_count(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"status": "in_progress"})
    assert response.json()["total"] == 6


def test_page_and_page_size_first_page(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page": 1, "page_size": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(seed_exchanges)
    assert len(data["items"]) == 3


def test_page_and_page_size_second_page(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page": 2, "page_size": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 12
    assert len(data["items"]) == 5


def test_page_and_page_size_last_partial_page(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page": 3, "page_size": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 12
    assert len(data["items"]) == 2


def test_page_out_of_range_returns_empty(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page": 99, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 12
    assert len(data["items"]) == 0


def test_default_page_size_value(client, seed_exchanges):
    response = client.get("/api/exchanges")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10


def test_pagination_ordered_by_id_desc(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page": 1, "page_size": 12})
    data = response.json()
    ids = [item["id"] for item in data["items"]]
    assert ids == sorted(ids, reverse=True)


def test_items_structure_fields(client, seed_exchanges):
    response = client.get("/api/exchanges", params={"page_size": 1})
    data = response.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert isinstance(item["id"], int)
    assert isinstance(item["book_title"], str)
    assert isinstance(item["counterpart_nickname"], str)
    assert isinstance(item["is_completed"], bool)
    assert "sent_date" in item
    assert "received_date" in item
    assert "notes" in item


def test_total_consistency_with_filters(client, seed_exchanges):
    no_filter = client.get("/api/exchanges").json()["total"]
    keyword_filter = client.get("/api/exchanges", params={"keyword": "平凡的世界"}).json()["total"]
    status_filter = client.get("/api/exchanges", params={"status": "completed"}).json()["total"]
    combined_filter = client.get(
        "/api/exchanges",
        params={"keyword": "三体", "status": "completed"},
    ).json()["total"]

    assert no_filter == 12
    assert keyword_filter == 3
    assert status_filter == 6
    assert combined_filter == 2


def test_combined_filters_keyword_and_status(client, seed_exchanges):
    response = client.get(
        "/api/exchanges",
        params={"keyword": "三体", "status": "completed"},
    )
    data = response.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert "三体" in item["book_title"]
        assert item["is_completed"] is True


def test_combined_filters_with_pagination(client, seed_exchanges):
    response = client.get(
        "/api/exchanges",
        params={"keyword": "平凡的世界", "page": 1, "page_size": 2},
    )
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert "平凡的世界" in item["book_title"]


def test_response_status_code_always_200(client, seed_exchanges):
    cases = [
        {},
        {"keyword": "三体"},
        {"status": "completed"},
        {"status": "in_progress"},
        {"page": 1, "page_size": 5},
        {"keyword": "X", "status": "completed", "page": 1, "page_size": 100},
    ]
    for params in cases:
        resp = client.get("/api/exchanges", params=params)
        assert resp.status_code == 200, f"params={params}"
