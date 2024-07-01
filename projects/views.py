from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Project
from projectService.utils.mongodb import get_mongo_db
from bson.objectid import ObjectId

# Initialize MongoDB collection
mongo_db = get_mongo_db()
collection = mongo_db['projects']

class ProjectViewSet(viewsets.ViewSet):
    
    def create(self, request):
        data = request.data
        required_fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project(**data)
            collection.insert_one(project.to_dict())
            return Response(project.to_dict(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to create project: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


