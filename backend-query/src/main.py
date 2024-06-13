import asyncio
from contextlib import asynccontextmanager
from enum import StrEnum
from typing import Any

from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from confluent_kafka import Consumer, KafkaException, KafkaError
from fastapi import FastAPI
from pydantic import BaseModel
from .model import Task_Pydantic, Task

conf = {
    "bootstrap.servers": "kafka-cluster.default.svc.cluster.local:9092",
    "group.id": "task-group",
}

TOPIC = "task-events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = Consumer(conf)
    task = basic_consume_loop(consumer, [TOPIC])
    asyncio.create_task(task)
    yield
    consumer.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "*",
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
    db_url="postgres://postgres:password@postgres.default.svc.cluster.local:5432/mydatabase",
    modules={"models": ["app.src.model"]},
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
    task: Task_Pydantic


async def process_event(event: dict[str, Any]):
    if event["action"] == Action.ADD:
        description = event["task"]
        task = Task(description=description)
        await task.save()
        return "saved"

    elif event["action"] == Action.REMOVE:
        id = event["task"]["id"]

        task = await Task.filter(id=id).first()
        if task:
            await task.delete()
        return "deleted"


async def basic_consume_loop(consumer, topics):
    consumer.subscribe(topics)

    try:
        while True:
            await asyncio.sleep(0.1)
            msg = consumer.poll(timeout=1)
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
                    event = eval(msg.value().decode())
                    _ = await process_event(event)
                except Exception:
                    print("Error processing")
    except Exception as e:
        print(f"Error in consumer loop: {e}")

    finally:
        consumer.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
