import json
from enum import StrEnum

import uvicorn
from confluent_kafka import Producer
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

conf = {"bootstrap.servers": "PLAINTEXT://kafka-cluster.default.svc.cluster.local:9092"}
producer = Producer(conf)

TOPIC = "task-events"

app = FastAPI()

origins = [
    "http://localhost:4200",
    "http://todo.local:80",
    "http://todo.local",
    "http://todo-ui.default.svc.cluster.local"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


class Action(StrEnum):
    ADD = "add"
    REMOVE = "remove"


class Task(BaseModel):
    id: int = Field(default=None)
    description: str
    created_at: str = Field(default=None)


def delivery_callback(err, msg):
    print("Message delivery succeeded: %s", msg)


tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post("/")
async def add_task(task: Task):
    producer.produce(
        TOPIC,
        json.dumps({"action": Action.ADD, "task": task.description}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task added"}


@tasks_router.delete("/")
async def remove_task(task: Task):
    producer.produce(
        "task-events",
        json.dumps({"action": Action.REMOVE, "task": task.model_dump()}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task removed"}


app.include_router(tasks_router)

if __name__ == "__main__":
    uvicorn.run(app)
