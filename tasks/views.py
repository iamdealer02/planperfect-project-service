from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task  
from projectService.utils.mongodb import get_mongo_db
from bson import ObjectId
from datetime import datetime

mongo_db = get_mongo_db()
tasks_collection = mongo_db['tasks']
projects_collection = mongo_db['projects']  
team_collection = mongo_db['teams']

# Create your views here.
class TaskViewSet(viewsets.ViewSet):

    # Create a task for a project with the current user as the assignee
    @action(methods=['post'], detail=False, url_path='(?P<pk>[0-9a-fA-F]{24})/create')
    def create_task(self, request, pk=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user_id = request.user.get('user_id')
            data = request.data
            required_fields = ['task_name']
            extra_fields = ['due_date', 'asignee_id', 'task_description']  # Added `asignee_id` for consistency

            # Check that required fields are present
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate `pk` and check that it is a valid ObjectId
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the project exists
            project = projects_collection.find_one({'_id': ObjectId(pk)})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user is a member or owner of the project
            user_team = team_collection.find_one({'project_id': ObjectId(pk), 'member_id': user_id})
            user_owned_project = projects_collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            if user_team is None and user_owned_project is None:
                return Response({'error': 'You are not a member of the project'}, status=status.HTTP_403_FORBIDDEN)

            # Add `project_id` and `asignee_id` to the task data
            data['project_id'] = str(pk)
            data['asignee_id'] = user_id
            
            # Insert the task into the tasks collection
            result = tasks_collection.insert_one(data)
            inserted_task = tasks_collection.find_one({'_id': result.inserted_id})

            # Convert the task to a dictionary and remove `_id` field from the response
            task_dict = Task.from_dict(inserted_task).to_dict()
            print(type(task_dict['_id']))
            return Response(task_dict, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Error creating task: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Assign the task to a user or patch update the task
    @action(methods=['patch'], detail=False, url_path='(?P<pk>[0-9a-fA-F]{24})/tasks/(?P<task_id>[0-9a-fA-F]{24})/update')
    def update_task(self, request, pk=None, task_id=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            data = request.data
            project_id = pk
            if not ObjectId.is_valid(project_id) or not ObjectId.is_valid(task_id):
                return Response({'error': 'Invalid project id or task id'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the project_id exists in the projects database
            project = projects_collection.find_one({'_id': ObjectId(project_id)})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
            # Ensure the user is a member or owner of the project
            user_team = team_collection.find_one({'project_id': ObjectId(project_id), 'member_id': user_id})
            user_owned_project = projects_collection.find_one({'_id': ObjectId(project_id), 'user_id': user_id})
            if user_team is None and user_owned_project is None:
                return Response({'error': 'You are not a member of the project'}, status=status.HTTP_403_FORBIDDEN)
            try:
               
                task = tasks_collection.find_one({'_id': ObjectId(task_id)})
                if task is None:
                    return Response({'error': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
                updated_task = tasks_collection.update_one({'_id': ObjectId(task_id)}, {'$set': {**data, 'updated_at': datetime.now()}})
                if updated_task.modified_count == 0:
                    return Response({'error': 'Error updating task'}, status=status.HTTP_400_BAD_REQUEST)
                updated_task = tasks_collection.find_one({'_id': ObjectId(task_id)})
                result = Task.from_dict(updated_task).to_dict()
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Error updating task: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error updating task: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # View all the tasks for a project
    @action(methods=['get'], detail=False, url_path='(?P<pk>[0-9a-fA-F]{24})/tasks')
    def list_tasks(self, request, pk=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            project_id = pk
            if not ObjectId.is_valid(project_id):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the project_id exists in the projects database
            project = projects_collection.find_one({'_id': ObjectId(project_id)})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
            # Ensure the user is a member or owner of the project
            user_team = team_collection.find_one({'project_id': ObjectId(project_id), 'member_id': user_id})
            user_owned_project = projects_collection.find_one({'_id': ObjectId(project_id), 'user_id': user_id})
            if user_team is None and user_owned_project is None:
                return Response({'error': 'You are not a member of the project'}, status=status.HTTP_403_FORBIDDEN)
           
            tasks = list(tasks_collection.find({'project_id': project_id}))

            result = [Task.from_dict(task).to_dict() for task in tasks]
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error retrieving tasks: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Get details of a specific task
    @action(methods=['get'], detail=False, url_path='(?P<pk>[0-9a-fA-F]{24})/tasks/(?P<task_id>[0-9a-fA-F]{24})')
    def view_task(self, request, pk=None, task_id=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            project_id = pk
            if not ObjectId.is_valid(project_id) or not ObjectId.is_valid(task_id):
                return Response({'error': 'Invalid project id or task id'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the project_id exists in the projects database
            project = projects_collection.find_one({'_id': ObjectId(project_id)})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
            # Ensure the user is a member or owner of the project
            user_team = team_collection.find_one({'project_id': ObjectId(project_id), 'member_id': user_id})
            user_owned_project = projects_collection.find_one({'_id': ObjectId(project_id), 'user_id': user_id})
            if user_team is None and user_owned_project is None:
                return Response({'error': 'You are not a member of the project'}, status=status.HTTP_403_FORBIDDEN)
            task = tasks_collection.find_one({'_id': ObjectId(task_id)})
            if task is None:
                return Response({'error': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
            result = Task.from_dict(task).to_dict()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error retrieving task: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Delete a specific task
    @action(methods=['delete'], detail=False, url_path='(?P<pk>[0-9a-fA-F]{24})/tasks/(?P<task_id>[0-9a-fA-F]{24})/delete')
    def delete_task(self, request, pk=None, task_id=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            project_id = pk
            if not ObjectId.is_valid(project_id) or not ObjectId.is_valid(task_id):
                return Response({'error': 'Invalid project id or task id'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the project_id exists in the projects database
            project = projects_collection.find_one({'_id': ObjectId(project_id)})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)
            # Ensure the user is a member or owner of the project
            user_team = team_collection.find_one({'project_id': ObjectId(project_id), 'member_id': user_id})
            user_owned_project = projects_collection.find_one({'_id': ObjectId(project_id), 'user_id': user_id})
            if user_team is None and user_owned_project is None:
                return Response({'error': 'You are not a member of the project'}, status=status.HTTP_403_FORBIDDEN)
            result = tasks_collection.delete_one({'_id': ObjectId(task_id)})
            if result.deleted_count == 0:
                return Response({'error': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error deleting task: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
