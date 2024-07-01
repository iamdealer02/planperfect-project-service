# because this is Mongo model without orms we do not need models from django

class Team:
    # add team member to ur project
    def __init__(self, project_id, member_id, role):
        self.project_id = project_id
        self.member_id = member_id
        self.role = role
    
    def to_dict(self):
        return {
            'project_id': self.project_id,
            'member_id': self.member_id,
            'role': self.role
        }
    
    @staticmethod
    def from_dict(data):
        return Team(
            project_id=data['project_id'],
            member_id=data['member_id'],
            role=data['role']
        )
    