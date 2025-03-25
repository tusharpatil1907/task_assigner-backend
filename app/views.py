from rest_framework import generics
from rest_framework.views import APIView
from .models import User, Task,Status,RequestTask
from .serializers import RequestTaskSerializer, UserSerializer, TaskSerializer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from django.utils import timezone
from django.shortcuts import get_object_or_404


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    


class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class UserAssignedTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        tasks = user.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data['id'])
        tokens = get_tokens_for_user(user)
        return Response({
            'user': response.data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


class CreateUpdateTaskView(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        if self.kwargs.get('pk'):
            return super().get_object()
        return None

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


# for user to update the status

class UpdateTaskStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_users=request.user)
        status_name = request.data.get('status')
        
        if not status_name:
            return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            status_obj = Status.objects.get(TaskStatus=status_name)
        except Status.DoesNotExist:
            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        task.status = status_obj
        task.updated_at = timezone.now()  
        task.save()
        
        return Response({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "users": [user.username for user in task.assigned_users.all()],
            "status": task.status.TaskStatus
        }, status=status.HTTP_200_OK)




class AssignTaskAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request):
        user_id = request.data.get('user_id')
        task_id = request.data.get('task_id')

        if not user_id or not task_id:
            return Response({'error': 'user_id and task_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(user_id, int) or not isinstance(task_id, int):
            return Response({'error': 'user_id and task_id must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            task = Task.objects.get(id=task_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.tasks.add(task)
        user.save()

        return Response({
            'message': f'Task "{task.title}" assigned to {user.username} successfully.',
            'user_id': user.id,
            'task_id': task.id
        }, status=status.HTTP_201_CREATED)


class UnassignOrReassignTaskAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request):
        user_id = request.data.get('user_id')
        task_id = request.data.get('task_id')
        reassign_to = request.data.get('reassign_to')

        if not user_id or not task_id:
            return Response({'error': 'user_id and task_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            task = Task.objects.get(id=task_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        if task not in user.tasks.all():
            return Response({
                'error': f'Task "{task.title}" is not assigned to {user.username}.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.tasks.remove(task)
        user.save()

        if reassign_to:
            try:
                new_user = User.objects.get(id=reassign_to)
                new_user.tasks.add(task)
                new_user.save()
                return Response({
                    'message': f'Task "{task.title}" reassigned from {user.username} to {new_user.username} successfully.',
                    'task_id': task.id,
                    'previous_user_id': user.id,
                    'new_user_id': new_user.id
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'New user to reassign not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': f'Task "{task.title}" unassigned from {user.username} successfully.',
            'task_id': task.id,
            'previous_user_id': user.id
        }, status=status.HTTP_200_OK)


class DeleteTaskAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task.assigned_users.clear()
            task.delete()
            return Response({'message': f'Task {task.title} deleted and unassigned from all users.'},
                            status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

class CreateRequestTaskAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Any authenticated user
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request):
        serializer = RequestTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response({
                'message': 'Request task created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetRequestTaskAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        # If the user is a superuser, show all requests
        if request.user.is_superuser:
            request_tasks = RequestTask.objects.all()
        else:
            # Else show only their own requests
            request_tasks = RequestTask.objects.filter(user=request.user)
        
        serializer = RequestTaskSerializer(request_tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ApproveRejectRequestTaskAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request):
        request_id = request.data.get('request_id')
        is_approved = request.data.get('is_approved')

        if request_id is None or is_approved is None:
            return Response({
                'error': 'Both request_id and is_approved are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_task = RequestTask.objects.get(request_ID=request_id)
        except RequestTask.DoesNotExist:
            return Response({
                'error': 'RequestTask not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        user = request_task.user_ID
        tasks = request_task.task_ID.all()

        if is_approved:
            for task in tasks:
                user.tasks.add(task)
                user.save()

            message = f"Request {request_id} approved. Task(s) assigned to {user.username}."
        else:
            request_task.delete()
            message = f"Request {request_id} rejected and removed."

        return Response({
            'message': message,
            'request_id': request_id,
            'user_id': user.id,
            'task_ids': [task.id for task in tasks] if is_approved else []
        }, status=status.HTTP_200_OK)


class DeleteOwnRequestTaskAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    def delete(self, request, request_id):
        try:
            request_task = RequestTask.objects.get(request_ID=request_id, user_ID=request.user)
        except RequestTask.DoesNotExist:
            return Response({
                'error': 'RequestTask not found or you do not have permission to delete this request.'
            }, status=status.HTTP_404_NOT_FOUND)

        request_task.delete()
        return Response({
            'message': f'Request {request_id} deleted successfully.'
        }, status=status.HTTP_200_OK)
