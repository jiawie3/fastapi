import os
import sys

# 把项目根目录（fastapi 这一层）加进 Python 搜索路径
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth_headers_for_user(
    username:str,
    password:str,
    email:str|None = None
    ) -> dict:
    """
    auth_headers_for_user:
    为某个用户：
    - 如果没注册过，就先注册
    - 然后登录，拿到 access_token
    - 返回带 Authorization 头的 headers 字典
    """
    if email is None:
        email = f"{username}@example.com"
    #1.注册，（如果已经注册过这里可能400，可以根据需要做处理）
    client.post(
        "/auth/register",
        json={
            "username":username,
            "password":password,
            "email":email,
        },
    )
    #2.登录，form表单而非json
    resp = client.post(
        "/auth/login",
        data={"username":username,"password":password},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    #3.拼出authorization头
    return {"Authorization":f"Bearer {token}"}



def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_tasks():
    #新增为了用户登录
    headers = auth_headers_for_user("user_list","password123")

    payload = {
        "title" : "测试任务",
        "description" : "from pytest",
        "is_done": False,
        "priority" : 3,
    }
    response_create = client.post("/tasks",json=payload,headers=headers)#新增headers
    
    assert response_create.status_code == 200
    data = response_create.json()
    assert data["title"] == "测试任务"
    assert data["description"] == "from pytest"
    assert data["is_done"] is False
    assert data["priority"] == 3
    task_id = data["id"]

    response_list = client.get("/tasks",headers=headers)#新增headers
    assert response_list.status_code == 200
    tasks = response_list.json()
    assert any(t['id'] == task_id for t in tasks)

def test_unauthorized_cant_access_tasks():
    """
    为登录状态下访问/tasks,返回401
    """
    resp_list = client.get("/tasks")
    assert resp_list.status_code ==401
    resp_create = client.post(
        "/tasks",
        json={"title":"x","is_done":False,"priority":1},
        )
    assert resp_create.status_code == 401

def test_other_user_cannot_access_my_task():
    """
    A 用户创建的任务，B 用户无法访问、修改、删除。
    """

    # A 登录并创建一个任务
    headers_a = auth_headers_for_user("userA", "passA123")
    create_resp = client.post(
        "/tasks",
        json={
            "title": "A's task",
            "is_done": False,
            "priority": 1,
        },
        headers=headers_a,
    )
    assert create_resp.status_code == 200
    task_id = create_resp.json()["id"]

    # B 登录
    headers_b = auth_headers_for_user("userB", "passB123")

    # B 访问 A 的任务详情 -> 应该 404（对 B 来说这个任务“不存在”）
    get_resp = client.get(f"/tasks/{task_id}", headers=headers_b)
    assert get_resp.status_code == 404

    # B 尝试修改 A 的任务 -> 404
    update_resp = client.put(
        f"/tasks/{task_id}",
        json={"title": "hacked"},
        headers=headers_b,
    )
    assert update_resp.status_code == 404

    # B 尝试删除 A 的任务 -> 404
    delete_resp = client.delete(f"/tasks/{task_id}", headers=headers_b)
    assert delete_resp.status_code == 404


def test_filter_done():
    headers = auth_headers_for_user("user_filter","passFilter123")
    payload1 = {
        "title" : "done",
        "is_done": True,
    }
    payload2 = {
        "title":"undone",
        "is_done":False,
    }
    
    response_done = client.post("/tasks",json=payload1,headers=headers)#add
    response_undone = client.post("/tasks",json=payload2,headers=headers)#add
    assert response_done.status_code == 200
    assert response_undone.status_code == 200

    resp_done = client.get("/tasks",params={"done":True},headers=headers)#add
    assert resp_done.status_code == 200
    task_done = resp_done.json()
    assert isinstance(task_done,list)
    assert any(t['title'] == "done" for t in task_done)
    assert all(t['is_done'] is True for t in task_done)
    
    resp_undone = client.get("/tasks",params={"done":False},headers=headers)#add
    assert resp_undone.status_code == 200
    task_undone = resp_undone.json()
    assert isinstance(task_undone,list)
    assert any(t['title'] == "undone" for t in task_undone)
    assert all(t['is_done'] is False for t in task_undone)

def test_keyword_search():
    
    headers = auth_headers_for_user("user_keyword","passKey123")

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
    resp_vip = client.post("/tasks",json=payload_keyword1,headers=headers)#add
    resp_normal = client.post("/tasks",json=payload_keyword2,headers=headers)#add

    assert resp_vip.status_code == 200
    assert resp_normal.status_code == 200
    response_search = client.get("/tasks",params={"keyword":"vip"},headers=headers)#add
    assert response_search.status_code == 200
    task_vip = response_search.json()
    assert isinstance(task_vip,list)
    assert any("vip" in t["title"] for t in task_vip)

def test_skip_limit():

    headers = auth_headers_for_user("user_pagination","passPage123")

    for i in range(10):
        resp = client.post("/tasks",json={
            "title":f"task-{i}",
            "priority":3, },
            headers = headers,
        )
        assert resp.status_code == 200
    response_skip_limit = client.get("/tasks",params={"skip":5,"limit":3},headers=headers)#add
    assert response_skip_limit.status_code == 200

def test_error_priority():

    headers = auth_headers_for_user("user_priority","passpri123")

    payload = {
        "title":"this is error priority",
        "priority": 6000,
    }
    response_error_priority = client.post("/tasks",json=payload,headers=headers)#add
    assert response_error_priority.status_code == 422

def test_update_task():

    headers = auth_headers_for_user("user_update","passUpdate123")

    # 1. 先创建一条任务
    payload = {
        "title": "before update",
        "description": "old desc",
        "is_done": False,
        "priority": 1,
    }
    resp_create = client.post("/tasks", json=payload,headers=headers)#add
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
    resp_update = client.put(f"/tasks/{task_id}", json=update_payload,headers=headers)#add
    assert resp_update.status_code == 200
    updated = resp_update.json()

    # 3. 断言字段真的被更新了
    assert updated["id"] == task_id              # id 不变
    assert updated["title"] == "after update"
    assert updated["description"] == "new desc"
    assert updated["is_done"] is True
    assert updated["priority"] == 5

def test_delete_task():

    headers = auth_headers_for_user("user_delete","passDel123")

    # 1. 先创建一条任务
    payload = {
        "title": "to be deleted",
        "description": "will be deleted",
        "is_done": False,
        "priority": 2,
    }
    resp_create = client.post("/tasks", json=payload,headers=headers)#add
    assert resp_create.status_code == 200
    task_id = resp_create.json()["id"]

    # 2. 调用删除接口
    resp_delete = client.delete(f"/tasks/{task_id}",headers=headers)#add
    assert resp_delete.status_code == 200
    assert resp_delete.json() == {"ok": True}

    # 3. 再查这条任务，应该返回 404
    resp_get = client.get(f"/tasks/{task_id}",headers=headers)#add
    assert resp_get.status_code == 404
