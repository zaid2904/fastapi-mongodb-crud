from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection


class ItemCreate(BaseModel):
    title: str
    description: str = ""


class ItemUpdate(BaseModel):
    title: str
    description: str = ""


class Item(BaseModel):
    id: str
    title: str
    description: str = ""


class MongoItemRepository:
    def __init__(self, collection: Collection[Any]) -> None:
        self.collection = collection

    @staticmethod
    def _serialize(document: dict[str, Any]) -> Item:
        return Item(
            id=str(document["_id"]),
            title=document["title"],
            description=document.get("description", ""),
        )

    def list_items(self) -> list[Item]:
        return [self._serialize(document) for document in self.collection.find().sort("_id", -1)]

    def create_item(self, item: ItemCreate) -> Item:
        result = self.collection.insert_one(item.model_dump())
        created = self.collection.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="Unable to create item")
        return self._serialize(created)

    def get_item(self, item_id: str) -> Item | None:
        if not ObjectId.is_valid(item_id):
            return None
        document = self.collection.find_one({"_id": ObjectId(item_id)})
        if not document:
            return None
        return self._serialize(document)

    def update_item(self, item_id: str, item: ItemUpdate) -> Item | None:
        if not ObjectId.is_valid(item_id):
            return None
        self.collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.model_dump()})
        updated = self.collection.find_one({"_id": ObjectId(item_id)})
        if not updated:
            return None
        return self._serialize(updated)

    def delete_item(self, item_id: str) -> bool:
        if not ObjectId.is_valid(item_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count == 1


@lru_cache(maxsize=1)
def get_repository() -> MongoItemRepository:
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("MONGODB_DB", "fastapi_crud")
    client = MongoClient(mongodb_url)
    collection = client[database_name]["items"]
    return MongoItemRepository(collection)


app = FastAPI(title="FastAPI MongoDB CRUD")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/api/items", response_model=list[Item])
def list_items(repository: MongoItemRepository = Depends(get_repository)) -> list[Item]:
    return repository.list_items()


@app.post("/api/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, repository: MongoItemRepository = Depends(get_repository)) -> Item:
    return repository.create_item(item)


@app.get("/api/items/{item_id}", response_model=Item)
def get_item(item_id: str, repository: MongoItemRepository = Depends(get_repository)) -> Item:
    item = repository.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/api/items/{item_id}", response_model=Item)
def update_item(item_id: str, item: ItemUpdate, repository: MongoItemRepository = Depends(get_repository)) -> Item:
    updated_item = repository.update_item(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, repository: MongoItemRepository = Depends(get_repository)) -> Response:
    deleted = repository.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
