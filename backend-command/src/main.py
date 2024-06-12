import json

import uvicorn
from confluent_kafka import Producer
from fastapi import FastAPI

conf = {"bootstrap.servers": "PLAINTEXT://localhost:9092"}
producer = Producer(conf)

TOPIC = "task-events"

app = FastAPI()


def delivery_callback(err, msg):
    print("Message delivery succeeded: %s", msg)


@app.post("/add")
async def add_task(task: dict):
    producer.produce(
        TOPIC,
        json.dumps({"action": "add", "task": task["task"]}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task added"}


@app.post("/remove")
async def remove_task(task: dict):
    producer.produce(
        "task-events",
        json.dumps({"action": "add", "task": task["task"]}),
        callback=delivery_callback,
    )
    producer.flush()
    return {"message": "Task removed"}


if __name__ == "__main__":
    uvicorn.run(app)
