from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Project  # Ensure the Project class is imported correctly
from projectService.utils.mongodb import get_mongo_db
from bson import ObjectId  # Ensure ObjectId is imported

# Initialize MongoDB collection
mongo_db = get_mongo_db()
collection = mongo_db['projects']

class ProjectViewSet(viewsets.ViewSet):
    def list(self, request):
        projects = collection.find()
        response = [Project.from_dict(project).to_dict() for project in projects]
        return Response(response)

    def retrieve(self, request, pk=None):
        try:
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            project = collection.find_one({'_id': ObjectId(pk)})
            if project is None:
                return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(Project.from_dict(project).to_dict())
        except Exception as e:
            return Response({'error': f'Error retrieving project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data = request.data
        required_fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # insert first and then the result (with mongo generated id will be put in the project class)
            result = collection.insert_one(data)
            project = collection.find_one({'_id': result.inserted_id})
            return Response(Project.from_dict(project).to_dict(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to create project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
    # delete method
    def destroy(self, request, pk=None):
        try:
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            result = collection.delete_one({'_id': ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Project deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': f'Failed to delete project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

