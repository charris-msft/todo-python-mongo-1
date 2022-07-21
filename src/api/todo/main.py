from datetime import datetime
from doctest import debug_script
from enum import Enum
from typing import List, Optional
from xmlrpc.client import DateTime
import sqlalchemy
from sqlalchemy import Column, MetaData, Table
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .database import database, engine

metadata = MetaData()


class TodoState(Enum):
    TODO = "todo"
    INPROGRESS = "inprogress"
    DONE = "done"


items = Table(
    "items",
    metadata,
    # Column("id", sqlalchemy.Integer, primary_key=True),
    Column("name", sqlalchemy.String),
    Column("description", sqlalchemy.String),
    # TODO - state may not work as a String
    Column("state", sqlalchemy.String),
    Column("dueDate", sqlalchemy.DateTime),
    Column("completedDate", sqlalchemy.DateTime),
    Column("createdDate", sqlalchemy.DateTime),
    Column("updatedDate", sqlalchemy.DateTime),
    Column("listId", sqlalchemy.Integer)
)

todoLists = Table(
    "todoLists",
    metadata,
    Column("id", sqlalchemy.Integer, primary_key=True),
    Column("name", sqlalchemy.String),
    Column("description", sqlalchemy.String),
    Column("createdDate", sqlalchemy.DateTime),
    Column("updatedDate", sqlalchemy.DateTime)
)

metadata.create_all(engine)


class ItemIn(BaseModel):
    name:        str
    description: Optional[str]
    state:       Optional[str]
    dueDate:     Optional[datetime]
    listId:      Optional[int]

class Item(BaseModel):
    name:        str
    description: Optional[str]
    state:       Optional[str]
    dueDate:     Optional[datetime]
    createdDate: Optional[datetime]
    updatedDate: Optional[datetime]
    listId:      Optional[int]

class TodoListIn(BaseModel):
    name:        str
    description: Optional[str]

class TodoList(BaseModel):
    id:          int
    name:        str
    description: Optional[str]

app = FastAPI(title = "REST API using FastAPI PostgreSQL Async EndPoints")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/items/", response_model=List[Item], status_code = status.HTTP_200_OK)
async def read_items(skip: int = 0, take: int = 20):
    query = items.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/items/{item_id}/", response_model=Item, status_code = status.HTTP_200_OK)
async def read_items(item_id: int):
    query = items.select().where(items.c.id == item_id)
    return await database.fetch_one(query)

@app.post("/items/", response_model=Item, status_code = status.HTTP_201_CREATED)
async def create_item(item: ItemIn):
    query = items.insert().values(name=item.name, state=item.state)
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}

@app.put("/items/{item_id}/", response_model=Item, status_code = status.HTTP_200_OK)
async def update_item(item_id: int, payload: ItemIn):
    query = items.update().where(items.c.id == item_id).values(name=payload.name, state=payload.state)
    await database.execute(query)
    return {**payload.dict(), "id": item_id}

@app.delete("/items/{item_id}/", status_code = status.HTTP_200_OK)
async def delete_item(item_id: int):
    query = items.delete().where(items.c.id == item_id)
    await database.execute(query)
    return {"message": "item with id: {} deleted successfully!".format(item_id)}


@app.get("/lists/", response_model=List[TodoList], status_code = status.HTTP_200_OK)
async def read_lists(skip: int = 0, take: int = 20):
    query = todoLists.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/lists/{list_id}/", response_model=TodoList, status_code = status.HTTP_200_OK)
async def read_lists(list_id: int):
    query = todoLists.select().where(todoLists.c.id == list_id)
    return await database.fetch_one(query)

@app.post("/lists/", response_model=TodoList, status_code = status.HTTP_201_CREATED)
async def create_list(list: TodoListIn):
    query = todoLists.insert().values(name=list.name, description=list.description)
    last_record_id = await database.execute(query)
    return {**list.dict(), "id": last_record_id}

@app.put("/lists/{list_id}/", response_model=TodoList, status_code = status.HTTP_200_OK)
async def update_list(list_id: int, payload: TodoListIn):
    query = todoLists.update().where(todoLists.c.id == list_id).values(name=payload.name, description=payload.description)
    await database.execute(query)
    return {**payload.dict(), "id": list_id}

@app.delete("/lists/{list_id}/", status_code = status.HTTP_200_OK)
async def delete_list(list_id: int):
    query = todoLists.delete().where(todoLists.c.id == list_id)
    await database.execute(query)
    return {"message": "list with id: {} deleted successfully!".format(list_id)}