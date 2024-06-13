import asyncio
import json
from contextlib import asynccontextmanager
from enum import StrEnum
from typing import Any, Dict

from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from confluent_kafka import Consumer, KafkaException, KafkaError
from fastapi import FastAPI
from pydantic import BaseModel
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from models import Task_Pydantic, Task



conf = {
    "bootstrap.servers": "kafka-cluster.default.svc.cluster.local:9092",
    "group.id": "task-group",
    "auto.offset.reset": "earliest",
}

TOPIC = "task-events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    consumer = Consumer(conf)
    loop.run_in_executor(None, basic_consume_loop, consumer, [TOPIC])
    yield
    consumer.close()


app = FastAPI(lifespan=lifespan)

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


register_tortoise(
    app,
    db_url="postgres://postgres.default.svc.cluster.local:5432/mydatabase",
    modules={"models": ["__main__"]},  # Ensure models are referenced correctly
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/tasks/")
async def get_tasks():
    tasks = await Task_Pydantic.from_queryset(Task.all())
    return tasks


class Action(StrEnum):
    ADD = "add"
    REMOVE = "remove"


class Event(BaseModel):
    action: Action
    task: TaskIn_Pydantic


async def process_event(event: Dict[str, Any]):
    if event["action"] == Action.ADD:
        description = event["task"]["description"]
        task = Task(description=description)
        await task.save()
        return "saved"

    elif event["action"] == Action.REMOVE:
        id = event["task"]["id"]
        task = await Task.filter(id=id).first()
        if task:
            await task.delete()
        return "deleted"


def basic_consume_loop(consumer, topics):
    consumer.subscribe(topics)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print("End of partition")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print("New message!")
                try:
                    event = json.loads(msg.value().decode())
                    loop.run_until_complete(process_event(event))
                except Exception as e:
                    print(f"Error processing: {e}")
    except Exception as e:
        print(f"Error in consumer loop: {e}")
    finally:
        consumer.close()
        loop.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
