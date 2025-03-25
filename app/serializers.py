from rest_framework import serializers
from .models import Task, User, Status,RequestTask
from django.contrib.auth.hashers import make_password



class TaskSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True, read_only=True) 
    status = serializers.CharField(source='status.TaskStatus', read_only=True)  

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'users', 'status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def create(self, validated_data):
        status = Status.objects.get_or_create(TaskStatus="New")[0]
        validated_data['status'] = status
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    assigned_tasks = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), many=True, write_only=True, required=False
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'tasks', 'assigned_tasks']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_password(self, value):
        """Add password validation if needed"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def create(self, validated_data):
        """Create user with hashed password"""
        tasks = validated_data.pop('assigned_tasks', [])
        validated_data['password'] = make_password(validated_data['password'])
        user = super().create(validated_data)
        user.tasks.set(tasks)  
        return user

    def update(self, instance, validated_data):
        """Update user and manage task assignment"""
        tasks = validated_data.pop('assigned_tasks', [])
        instance = super().update(instance, validated_data)
        if tasks:
            instance.tasks.set(tasks)  
        return instance


class RequestTaskSerializer(serializers.ModelSerializer):
    tasks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Task.objects.all()
    )

    class Meta:
        model = RequestTask
        fields = ['request_ID', 'user', 'tasks']

    def create(self, validated_data):
        tasks = validated_data.pop('tasks')
        request_task = RequestTask.objects.create(**validated_data)
        request_task.tasks.set(tasks)
        return request_task
