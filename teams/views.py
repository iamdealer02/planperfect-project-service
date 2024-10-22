from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Team  # Ensure the Team class is imported correctly
from projectService.utils.mongodb import get_mongo_db
from bson import ObjectId  # Ensure ObjectId is imported
from django.urls import path
# Create your views here.

mongo_db = get_mongo_db()
teams_collection = mongo_db['teams']
projects_collection = mongo_db['projects']  # Ensure this references the projects collection

class TeamViewSet(viewsets.ViewSet):

    def create(self, request):
        # Create a team

        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            data = request.data
            required_fields = ['project_id', 'member_id', 'role']
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the user is not adding themselves to the team
            if data['member_id'] == user_id:
                return Response({'error': 'You cannot add yourself to the team'}, status=status.HTTP_400_BAD_REQUEST)
            # Ensure the project_id exists in the projects database
            if not ObjectId.is_valid(data['project_id']):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            # user is the owner of the project
            user_owned_project = projects_collection.find_one({'_id': ObjectId(data['project_id']), 'user_id': user_id})
            if user_owned_project is None:
                return Response({'error': 'You are not the owner of the project'}, status=status.HTTP_403_FORBIDDEN)
            project_id = ObjectId(data['project_id'])
            project = projects_collection.find_one({'_id': project_id})
            if project is None:
                return Response({'error': 'Project does not exist'}, status=status.HTTP_404_NOT_FOUND)

            # Placeholder for user service check to see if the member_id exists
            user_exists = True  # Assume user exists for now
            if not user_exists:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

            try:
                # Insert first and then the result (with MongoDB generated id will be put in the project class)
                team = Team(project_id, data['member_id'], data['role'])
                result = teams_collection.insert_one(team.to_dict())
                # get the inserted team member
                inserted_team = teams_collection.find_one({'_id': result.inserted_id})
                result = Team.from_dict(inserted_team).to_dict()
                return Response(result, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': f'Error creating team: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error creating team: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
    
        # Retrieve all team members by project_id
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            # user is the owner of the project neither the team member
            user_id = request.user.get('user_id')
            user_owned_project = projects_collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            is_team_member = teams_collection.find_one({'project_id': pk, 'member_id': user_id})
            if user_owned_project is None and is_team_member is None:
                return Response({'error': 'You are not the owner of the project or a team member'}, status=status.HTTP_403_FORBIDDEN)
            # Finding all the team members in the project
            team_members = list(teams_collection.find({'project_id': pk}))
            if not team_members:
                return Response({'error': 'No team members found for this project'}, status=status.HTTP_404_NOT_FOUND)

            # Convert each team member document to a Team object and then to a dictionary
            team_members = [Team.from_dict(member).to_dict() for member in team_members]
            return Response(team_members, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error retrieving team members: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


# all the projects the user is in, the teans he belog to
    def list(self, request):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            # You can access payload data from the request.user attribute
            user_id = request.user.get('user_id')
            # for this user_id, get all the projects
            team_member = teams_collection.find({'member_id': user_id})
            # find the project details for the team
            team_project = []
            for team in team_member:
                project = projects_collection.find_one({'_id': team['project_id']})
                team['project'] = project
                team_project.append(team)
            
            response = [Team.from_dict(team).to_dict() for team in team_project]
            return Response(response)
        except Exception as e:
            return Response({'error': f'Unauthorized: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)
        

    @action(detail=True, methods=['put'], url_path='update-member/(?P<mid>[^/.]+)')
    def update_member(self, request, pk=None, mid=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            print(pk, mid)  # `mid` is just a string

            # Check if pk (project_id) is a valid ObjectId
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user is the owner of the project
            user_owned_project = projects_collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            if user_owned_project is None:
                return Response({'error': 'You are not the owner of the project'}, status=status.HTTP_403_FORBIDDEN)
            
            # Update the team member
            result = teams_collection.update_one(
                {'project_id': pk, 'member_id': mid},
                {'$set': request.data}
            )
            if result.matched_count == 0:
                return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)
            
            team = teams_collection.find({'project_id': pk})
            response = [Team.from_dict(member).to_dict() for member in team]
            return Response(response)
        except Exception as e:
            return Response({'error': f'Error updating team: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete-member/(?P<mid>[^/.]+)')
    def delete_member(self, request, pk=None, mid=None):
        if not hasattr(request, 'user') or not request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_id = request.user.get('user_id')
            if not ObjectId.is_valid(pk):
                return Response({'error': 'Invalid project id'}, status=status.HTTP_400_BAD_REQUEST)
            user_owned_project = projects_collection.find_one({'_id': ObjectId(pk), 'user_id': user_id})
            if user_owned_project is None:
                return Response({'error': 'You are not the owner of the project'}, status=status.HTTP_403_FORBIDDEN)
            
            # Delete the team member
            result = teams_collection.delete_one({'project_id': pk, 'member_id': mid})
            if result.deleted_count == 0:
                return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)
            
            team = teams_collection.find({'project_id': pk})
            response = [Team.from_dict(member).to_dict() for member in team]
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error deleting team: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<pk>/update-member/<mid>/', self.update_member, name='team-update-member'),
            path('<pk>/delete-member/<mid>/', self.delete_member, name='team-delete-member'),
        ]
        return urls + custom_urls