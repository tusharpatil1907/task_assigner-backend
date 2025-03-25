from django.urls import path
from .views import *
urlpatterns = [
    # User Registration
    path('register-user/', RegisterUserView.as_view(), name='register-user'),

    # Superuser-only APIs
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('delete-task/<int:task_id>/', DeleteTaskAPIView.as_view(), name='delete-task'),  

    # Logged-in user tasks
    path('my-tasks/', UserAssignedTasksView.as_view(), name='my-tasks'),

    # Create/Update Task (Superuser-only)
    path('create-task/', CreateUpdateTaskView.as_view()), 
    path('update-task/<int:pk>/', CreateUpdateTaskView.as_view()),

    # Task Assignment APIs (Superuser-only)
    path('assign-task/', AssignTaskAPIView.as_view(), name='assign'),
    path('unassign-or-reassigntask/', UnassignOrReassignTaskAPIView.as_view(), name='unassign-reassign'),  
    path('update-status/<int:pk>/', UpdateTaskStatusView.as_view(), name='update-status'),
    path('request-task/', CreateRequestTaskAPIView.as_view(), name='create-request-task'),
    path('task-assignment-requests/', GetRequestTaskAPIView.as_view(), name='task-assignment-requests'),
    path('task-approval/', ApproveRejectRequestTaskAPIView.as_view(), name='task-approval'),
    path('delete-request/', DeleteOwnRequestTaskAPIView.as_view(), name='task-request'),
]
