def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200

    data = r.json()
    assert data["status"] == "ok"
    assert data["timestamp"] is not None

def test_status_supported_languages(client):
    r = client.get("/status")
    assert r.status_code == 200

    data = r.json()
    assert data["status"] == "ok"
    assert data["timestamp"] is not None

    assert data["supported_languages"] == [
        "c",
        "cpp",
        "csharp",
        "go",
        "java",
        "javascript",
        "prompt",
        "python",
    ]

def test_extract_python_one_function(client):
    py = b"""\
def f(a: int, b) -> int:
    \"\"\"doc\"\"\"
    return a
"""
    r = client.post("/extract", files={"files": ("test.py", py, "text/x-python")})
    assert r.status_code == 200

    data = r.json()
    assert "results" in data
    assert len(data["results"]) == 1

    item = data["results"][0]
    assert item["file"] == "test.py"
    assert item["language"] == "python"
    assert item["count"] == 1
    assert item["functions"][0]["name"] == "f"
    assert item["functions"][0]["docstring"] == "doc"


def test_extract_unsupported_extension(client):
    r = client.post("/extract", files={"files": ("test.xyz", b"123", "application/octet-stream")})
    assert r.status_code == 200

    data = r.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["file"] == "test.xyz"
    assert data["results"][0]["error"] == "Unsupported file extension"


# import pytest
# from fastapi.testclient import TestClient
# from src.main import app

# @pytest.fixture
# def client():
#     return TestClient(app)

# def test_health_check(client):
#     """Тест здоровья сервиса"""
#     response = client.get("/health")
#     assert response.status_code == 200
#     assert response.json()["status"] == "ok"

# # def test_status_endpoint(client):
# #     """Тест информации о статусе"""
# #     response = client.get("/status")
# #     assert response.status_code == 200
# #     data = response.json()
# #     assert "supported_languages" in data
# #     assert len(data["supported_languages"]) > 0

# # def test_extract_python_file(client):
# #     """Тест выделения функций из Python"""
# #     python_code = b"""
# # def greet(name):
# #     return f"Hello {name}"
# # """
# #     response = client.post(
# #         "/extract",
# #         files={"file": ("test.py", python_code)}
# #     )
# #     assert response.status_code == 200
# #     data = response.json()
# #     assert data["language"] == "python"
# #     assert len(data["functions"]) == 1
# #     assert data["functions"]["name"] == "greet"