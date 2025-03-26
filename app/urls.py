from django.urls import path
from .views import *
urlpatterns = [
    # register as a user - anyone
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
    # retrive all users - superuser only 
    path('users/', UserListAPIView.as_view(), name='user-list'),
    # Create-task update task and delete task - super user only
    path('create-task/', CreateUpdateTaskView.as_view()), 
    path('update-task/<int:pk>/', CreateUpdateTaskView.as_view()),
    path('delete-task/<int:task_id>/', DeleteTaskAPIView.as_view(), name='delete-task'),
    # retrive taask lists - any logged in user.
    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('my-tasks/', UserAssignedTasksView.as_view(), name='my-tasks'),
    # assignment and unassignment of tasks - superuser only.
    path('assign-task/', AssignTaskAPIView.as_view(), name='assign'),
    path('unassign-or-reassigntask/', UnassignOrReassignTaskAPIView.as_view(), name='unassign-reassign'),
    # update status of task - normal user can change only assigned tasks  - superuser can change any record status.
    path('update-status/<int:pk>/', UpdateTaskStatusView.as_view(), name='update-status'),
    # requesting a task - any logged in user.
    path('request-task/', CreateRequestTaskAPIView.as_view(), name='create-request-task'),
    # Deleting task -only user can only delete their own created tasks.
    path('delete-request/<int:request_id>', DeleteOwnRequestTaskAPIView.as_view(), name='task-request'),
    # All assignment requests can be accessed by superuser whereas, user can only have access to created ones.
    path('task-assignment-requests/', GetRequestTaskAPIView.as_view(), name='task-assignment-requests'),
    # task approval and rejection can be done by superuser only
    path('task-approval/', ApproveRejectRequestTaskAPIView.as_view(), name='task-approval'),
]
