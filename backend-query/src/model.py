from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Task(models.Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)


Task_Pydantic = pydantic_model_creator(Task, name="Task")
TaskIn_Pydantic = pydantic_model_creator(Task, name="TaskIn", exclude_readonly=True)
