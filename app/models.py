from django.contrib.auth.models import AbstractUser
from django.db import models


class Status(models.Model):

    TaskStatus = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.TaskStatus


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, related_name='tasks')  

    def __str__(self):
        return self.title


class User(AbstractUser):
    tasks = models.ManyToManyField(Task, related_name='assigned_users', blank=True)

    def __str__(self):
        return self.username


class RequestTask(models.Model):
    request_ID = models.AutoField(primary_key=True)  
    user = models.ForeignKey(User, on_delete=models.PROTECT)  
    tasks = models.ManyToManyField(Task, related_name='request_tasks')

    def __str__(self):
        task_titles = ", ".join([task.title for task in self.tasks.all()])
        return f"Assign Request {self.request_ID}: {self.user.username} - {task_titles}"
