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

