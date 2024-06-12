import asyncio
from contextlib import asynccontextmanager
from enum import StrEnum
from tortoise.contrib.fastapi import register_tortoise
import uvicorn
from confluent_kafka import Consumer, KafkaException, KafkaError
from fastapi import FastAPI
from pydantic import BaseModel
from models import Task, Task_Pydantic

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "task-group",
    "auto.offset.reset": "earliest",
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

register_tortoise(
    app,
    db_url="postgres://postgres:password@localhost:5432/mydatabase",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/tasks")
async def get_tasks():
    tasks = await Task_Pydantic.from_queryset(Task.all())
    return tasks


class Action(StrEnum):
    ADD = "add"
    REMOVE = "remove"


class Event(BaseModel):
    action: Action
    task: str


async def process_event(event: Event):
    if event.action == Action.ADD:
        task = Task(description=event.task)
        await task.save()

    elif event.action == Action.REMOVE:
        task = await Task.filter(description=event.task).first()
        if task:
            await task.delete()


async def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while True:
            await asyncio.sleep(0.1)
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
                event = Event.parse_raw(msg.value().decode())
                await process_event(event)
    except Exception as e:
        print(f"Error in consumer loop: {e}")
    finally:
        consumer.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
