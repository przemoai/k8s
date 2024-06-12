import json
from enum import StrEnum

import uvicorn
from confluent_kafka import Producer
from fastapi import FastAPI
from pydantic import BaseModel

conf = {"bootstrap.servers": "PLAINTEXT://localhost:9092"}
producer = Producer(conf)

TOPIC = "task-events"

app = FastAPI()


class Action(StrEnum):
    ADD = "add"
    REMOVE = "remove"


class Task(BaseModel):
    title: str


def delivery_callback(err, msg):
    print("Message delivery succeeded: %s", msg)


@app.post("/add")
async def add_task(task: Task):
    producer.produce(
        TOPIC,
        json.dumps({"action": Action.ADD, "task": task.title}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task added"}


@app.post("/remove")
async def remove_task(task: Task):
    producer.produce(
        "task-events",
        json.dumps({"action": Action.REMOVE, "task": task.title}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task removed"}


if __name__ == "__main__":
    uvicorn.run(app)
