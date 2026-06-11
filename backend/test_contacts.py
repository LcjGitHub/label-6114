def test_create_contact(client):
    payload = {
        "nickname": "测试联系人",
        "contact_info": "test@example.com",
        "notes": "测试备注"
    }
    response = client.post("/api/contacts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nickname"] == "测试联系人"
    assert data["contact_info"] == "test@example.com"
    assert data["id"] is not None


def test_list_contacts(client):
    for i in range(3):
        client.post("/api/contacts", json={
            "nickname": f"联系人{i}",
            "contact_info": f"contact{i}@example.com",
        })
    response = client.get("/api/contacts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3


def test_get_contact(client):
    create_resp = client.post("/api/contacts", json={
        "nickname": "详情联系人",
        "contact_info": "detail@example.com",
    })
    contact_id = create_resp.json()["id"]
    response = client.get(f"/api/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["nickname"] == "详情联系人"


def test_get_contact_not_found(client):
    response = client.get("/api/contacts/99999")
    assert response.status_code == 404


def test_update_contact(client):
    create_resp = client.post("/api/contacts", json={
        "nickname": "更新前昵称",
        "contact_info": "old@example.com",
    })
    contact_id = create_resp.json()["id"]
    update_resp = client.put(f"/api/contacts/{contact_id}", json={
        "nickname": "更新后昵称",
        "contact_info": "new@example.com",
    })
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["nickname"] == "更新后昵称"
    assert updated["contact_info"] == "new@example.com"


def test_delete_contact(client):
    create_resp = client.post("/api/contacts", json={
        "nickname": "删除联系人",
        "contact_info": "delete@example.com",
    })
    contact_id = create_resp.json()["id"]
    del_resp = client.delete(f"/api/contacts/{contact_id}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/api/contacts/{contact_id}")
    assert get_resp.status_code == 404


def test_pagination_contacts(client):
    for i in range(15):
        client.post("/api/contacts", json={
            "nickname": f"分页联系人{i}",
            "contact_info": f"page{i}@example.com",
        })
    response = client.get("/api/contacts?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10

    response2 = client.get("/api/contacts?page=2&page_size=10")
    assert response2.status_code == 200


def test_search_contacts(client):
    client.post("/api/contacts", json={
        "nickname": "张三",
        "contact_info": "zhangsan@example.com",
    })
    client.post("/api/contacts", json={
        "nickname": "李四",
        "contact_info": "lisi@example.com",
    })
    client.post("/api/contacts", json={
        "nickname": "王五",
        "contact_info": "wangwu@test.com",
    })

    response = client.get("/api/contacts?keyword=张")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["nickname"] == "张三" for item in data["items"])

    response2 = client.get("/api/contacts?keyword=example.com")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["total"] >= 2
    nicknames = [item["nickname"] for item in data2["items"]]
    assert "张三" in nicknames
    assert "李四" in nicknames

    response3 = client.get("/api/contacts?keyword=不存在")
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["total"] == 0
