from datetime import date


def test_create_exchange(client):
    payload = {
        "book_title": "测试杂志",
        "counterpart_nickname": "测试用户",
        "sent_date": "2024-01-01",
        "received_date": "2024-01-15",
        "is_completed": True,
        "notes": "测试备注"
    }
    response = client.post("/api/exchanges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["book_title"] == "测试杂志"
    assert data["counterpart_nickname"] == "测试用户"
    assert data["is_completed"] is True
    assert data["id"] is not None


def test_list_exchanges(client):
    for i in range(3):
        client.post("/api/exchanges", json={
            "book_title": f"杂志{i}",
            "counterpart_nickname": f"用户{i}",
        })
    response = client.get("/api/exchanges")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3


def test_get_exchange(client):
    create_resp = client.post("/api/exchanges", json={
        "book_title": "详情测试",
        "counterpart_nickname": "详情用户",
    })
    exchange_id = create_resp.json()["id"]
    response = client.get(f"/api/exchanges/{exchange_id}")
    assert response.status_code == 200
    assert response.json()["book_title"] == "详情测试"


def test_get_exchange_not_found(client):
    response = client.get("/api/exchanges/99999")
    assert response.status_code == 404


def test_update_exchange(client):
    create_resp = client.post("/api/exchanges", json={
        "book_title": "更新前",
        "counterpart_nickname": "更新用户",
    })
    exchange_id = create_resp.json()["id"]
    update_resp = client.put(f"/api/exchanges/{exchange_id}", json={
        "book_title": "更新后"
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["book_title"] == "更新后"


def test_delete_exchange(client):
    create_resp = client.post("/api/exchanges", json={
        "book_title": "删除测试",
        "counterpart_nickname": "删除用户",
    })
    exchange_id = create_resp.json()["id"]
    del_resp = client.delete(f"/api/exchanges/{exchange_id}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/api/exchanges/{exchange_id}")
    assert get_resp.status_code == 404


def test_batch_delete_exchanges(client):
    ids = []
    for i in range(3):
        resp = client.post("/api/exchanges", json={
            "book_title": f"批量删除{i}",
            "counterpart_nickname": f"用户{i}",
        })
        ids.append(resp.json()["id"])
    batch_resp = client.post("/api/exchanges/batch-delete", json={"ids": ids})
    assert batch_resp.status_code == 204


def test_batch_delete_empty(client):
    response = client.post("/api/exchanges/batch-delete", json={"ids": []})
    assert response.status_code == 400


def test_get_statistics(client):
    response = client.get("/api/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "completed_count" in data
    assert "in_progress_count" in data
    assert data["total_count"] == data["completed_count"] + data["in_progress_count"]


def test_filter_exchanges_by_keyword(client):
    client.post("/api/exchanges", json={
        "book_title": "特殊关键词杂志",
        "counterpart_nickname": "特殊关键词用户",
    })
    response = client.get("/api/exchanges?keyword=关键词")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_filter_exchanges_by_status(client):
    client.post("/api/exchanges", json={
        "book_title": "已完成杂志",
        "counterpart_nickname": "用户A",
        "is_completed": True,
    })
    client.post("/api/exchanges", json={
        "book_title": "进行中杂志",
        "counterpart_nickname": "用户B",
        "is_completed": False,
    })
    completed_resp = client.get("/api/exchanges?status=completed")
    assert completed_resp.status_code == 200
    for item in completed_resp.json()["items"]:
        assert item["is_completed"] is True

    in_progress_resp = client.get("/api/exchanges?status=in_progress")
    assert in_progress_resp.status_code == 200
    for item in in_progress_resp.json()["items"]:
        assert item["is_completed"] is False


def test_export_exchanges_csv(client):
    client.post("/api/exchanges", json={
        "book_title": "导出测试",
        "counterpart_nickname": "导出用户",
        "sent_date": "2024-01-01",
        "is_completed": False,
    })
    response = client.get("/api/exchanges/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
