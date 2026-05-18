import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app, get_repository


class InMemoryRepository:
    def __init__(self):
        self.items = {}

    def list_items(self):
        return list(self.items.values())

    def create_item(self, item):
        item_id = str(uuid4())
        created = {"id": item_id, **item.model_dump()}
        self.items[item_id] = created
        from app.main import Item

        return Item(**created)

    def get_item(self, item_id):
        item = self.items.get(item_id)
        if not item:
            return None
        from app.main import Item

        return Item(**item)

    def update_item(self, item_id, item):
        if item_id not in self.items:
            return None
        self.items[item_id].update(item.model_dump())
        from app.main import Item

        return Item(**self.items[item_id])

    def delete_item(self, item_id):
        return self.items.pop(item_id, None) is not None


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        app.dependency_overrides[get_repository] = lambda: self.repo
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_crud_lifecycle(self):
        create_response = self.client.post(
            "/api/items", json={"title": "First", "description": "Item"}
        )
        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        item_id = created["id"]

        list_response = self.client.get("/api/items")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)

        update_response = self.client.put(
            f"/api/items/{item_id}",
            json={"title": "Updated", "description": "Changed"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["title"], "Updated")

        delete_response = self.client.delete(f"/api/items/{item_id}")
        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client.get(f"/api/items/{item_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_missing_item_returns_404(self):
        response = self.client.get("/api/items/missing")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
