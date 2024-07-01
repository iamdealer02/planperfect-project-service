from bson import ObjectId  # Import ObjectId to create and handle MongoDB IDs

class Project:
    def __init__(self, name, description, start_date, end_date, is_active, _id=None):
        self._id = _id if _id else ObjectId()  # Assign a new ObjectId if not provided
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active

    def to_dict(self):
        return {
            '_id': str(self._id),  # Convert ObjectId to string for JSON serialization
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data):
        # Create a Project instance from a dictionary including '_id'
        return Project(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            is_active=data['is_active'],
            _id=ObjectId(data['_id']) if '_id' in data else None
        )
