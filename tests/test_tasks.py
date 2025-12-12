import os
import sys

# 把项目根目录（fastapi 这一层）加进 Python 搜索路径
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
def test_list_tasks():
    payload = {
        "title" : "测试任务",
        "description" : "from pytest",
        "is_done": False,
        "priority" : 3,
    }
    response_create = client.post("/tasks",json=payload)

    assert response_create.status_code == 200
    data = response_create.json()
    assert data["title"] == "测试任务"
    assert data["description"] == "from pytest"
    assert data["is_done"] is False
    assert data["priority"] == 3
    task_id = data["id"]

    response_list = client.get("/tasks")
    assert response_list.status_code == 200
    tasks = response_list.json()
    assert any(t['id'] == task_id for t in tasks)
    print("返回",response_create.json())



def test_filter_done():
    payload1 = {
        "title" : "done",
        "is_done": True,
    }
    payload2 = {
        "title":"undone",
        "is_done":False,
    }
    
    response_done = client.post("/tasks",json=payload1)
    response_undone = client.post("/tasks",json=payload2)
    assert response_done.status_code == 200
    assert response_undone.status_code == 200

    resp_done = client.get("/tasks",params={"done":True})
    assert resp_done.status_code == 200
    task_done = resp_done.json()
    assert isinstance(task_done,list)
    assert any(t['title'] == "done" for t in task_done)
    assert all(t['is_done'] is True for t in task_done)
    
    resp_undone = client.get("/tasks",params={"done":False})
    assert resp_undone.status_code == 200
    task_undone = resp_undone.json()
    assert isinstance(task_undone,list)
    assert any(t['title'] == "undone" for t in task_undone)
    assert all(t['is_done'] is False for t in task_undone)

def test_keyword_search():
    payload_keyword1 = {
        "title":"vip",
        "description" : "this is vip member",
        "is_done": False,
        "priority":5,
    }
    payload_keyword2 ={
        "title":"normal",
        "description":"just a normal user",
        "is_done":False,
        "priority":2,
    }
    resp_vip = client.post("/tasks",json=payload_keyword1)
    resp_normal = client.post("/tasks",json=payload_keyword2)

    assert resp_vip.status_code == 200
    assert resp_normal.status_code == 200
    response_search = client.get("/tasks",params={"keyword":"vip"})
    assert response_search.status_code == 200
    task_vip = response_search.json()
    assert isinstance(task_vip,list)
    assert any("vip" in t["title"] for t in task_vip)

def test_skip_limit():
    for i in range(10):
        resp = client.post("/tasks",json={
            "title":f"task-{i}",
            "priority":3 ,
        })
        assert resp.status_code == 200
    response_skip_limit = client.get("/tasks",params={"skip":5,"limit":3})
    assert response_skip_limit.status_code == 200


def test_error_priority():
    payload = {
        "title":"this is error priority",
        "priority": 6000,
    }
    response_error_priority = client.post("/tasks",json=payload)
    assert response_error_priority.status_code == 422

def test_update_task():
    # 1. 先创建一条任务
    payload = {
        "title": "before update",
        "description": "old desc",
        "is_done": False,
        "priority": 1,
    }
    resp_create = client.post("/tasks", json=payload)
    assert resp_create.status_code == 200
    task = resp_create.json()
    task_id = task["id"]

    # 2. 调用更新接口，改几个字段
    update_payload = {
        "title": "after update",
        "description": "new desc",
        "is_done": True,
        "priority": 5,
    }
    resp_update = client.put(f"/tasks/{task_id}", json=update_payload)
    assert resp_update.status_code == 200
    updated = resp_update.json()

    # 3. 断言字段真的被更新了
    assert updated["id"] == task_id              # id 不变
    assert updated["title"] == "after update"
    assert updated["description"] == "new desc"
    assert updated["is_done"] is True
    assert updated["priority"] == 5

def test_delete_task():
    # 1. 先创建一条任务
    payload = {
        "title": "to be deleted",
        "description": "will be deleted",
        "is_done": False,
        "priority": 2,
    }
    resp_create = client.post("/tasks", json=payload)
    assert resp_create.status_code == 200
    task_id = resp_create.json()["id"]

    # 2. 调用删除接口
    resp_delete = client.delete(f"/tasks/{task_id}")
    assert resp_delete.status_code == 200
    assert resp_delete.json() == {"ok": True}

    # 3. 再查这条任务，应该返回 404
    resp_get = client.get(f"/tasks/{task_id}")
    assert resp_get.status_code == 404
