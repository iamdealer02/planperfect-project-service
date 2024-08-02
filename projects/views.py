from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Project  # Ensure the Project class is imported correctly
from projectService.utils.mongodb import get_mongo_db
from bson import ObjectId  # Ensure ObjectId is imported
# pyjwt decode the token

from django.views.decorators.csrf import csrf_exempt

# Initialize MongoDB collection
mongo_db = get_mongo_db()
collection = mongo_db['projects']

class ProjectViewSet(viewsets.ViewSet):

    def list(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # You can access payload data from the request.user attribute
            user_id = request.user.get('user_id')
            # for this user_id, get all the projects
            projects = collection.find({'user_id': user_id})
            response = [Project.from_dict(project).to_dict() for project in projects]
            return Response(response)
        except Exception as e:
            return Response({'error': f'Unauthorized: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user_id = request.user.get('user_id')
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            # user can only retrieve projects that belong to them
            project = collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            if project is None:
                return Response({'error': 'You do not have such Project'}, status=status.HTTP_404_NOT_FOUND)
            return Response(Project.from_dict(project).to_dict())
        except Exception as e:
            return Response({'error': f'Error retrieving project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    def create(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # You can access payload data from the request.user attribute
            user_id = request.user.get('user_id')
            data = request.data
            required_fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # insert first and then the result (with mongo generated id will be put in the project class)
                # add user_id to the data
                data['user_id'] = user_id
                result = collection.insert_one(data)
                project = collection.find_one({'_id': result.inserted_id})
                return Response(Project.from_dict(project).to_dict(), status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': f'Failed to create project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Unauthorized: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    def update(self, request, pk=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        if not ObjectId.is_valid(pk):
            return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        try:
            # user can only update projects that belong to them
            user_id = request.user.get('user_id')
            collection.update_one({'_id': ObjectId(pk)}, {'$set': data})
            project = collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            if project is None:
                return Response({'error': 'You do not have such Project'}, status=status.HTTP_404_NOT_FOUND)
            return Response(Project.from_dict(project).to_dict())
        except Exception as e:
            return Response({'error': f'Failed to update project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
    # delete method
    def destroy(self, request, pk=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            # user can only delete projects that belong to them
            user_id = request.user.get('user_id')
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            result = collection.delete_one({'_id': ObjectId(pk), 'user_id': user_id})
            if result.deleted_count == 0:
                return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Project deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to delete project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

