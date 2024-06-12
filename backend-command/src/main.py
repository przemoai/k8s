import json

from confluent_kafka import Producer
from fastapi import FastAPI

app = FastAPI()
conf = {'bootstrap.servers': 'kafka:9092'}

producer = Producer(conf)


@app.post("/add")
def add_task(task: dict):
    producer.produce('task-events', json.dumps({'action': 'add', 'task': task['task']}))
    return {"message": "Task added"}


@app.post("/remove")
def remove_task(task: dict):
    producer.produce('task-events', json.dumps({'action': 'add', 'task': task['task']}))
    return {"message": "Task removed"}
