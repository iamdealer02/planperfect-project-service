from datetime import datetime, timezone
from bson import ObjectId

class Task:
    def __init__(self, _id, task_name,project_id,asignee_id, task_description=None, task_status='initialized', created_at=None, updated_at=None, due_date=None, asigned_to=None):
        self._id = _id if _id else ObjectId()
        self.task_name = task_name
        self.task_description = task_description
        self.task_status = task_status
        self.asignee_id = asignee_id
        self.project_id = project_id
        self.created_at = created_at if created_at else datetime.now(timezone.utc) 
        self.updated_at = updated_at 
        self.due_date = due_date
        self.asigned_to = asigned_to

    def to_dict(self):
        return {
            '_id': str(self._id),
            'task_name': self.task_name,
            'task_description': self.task_description,
            'task_status': self.task_status,
            'asignee_id': self.asignee_id,
            'project_id': self.project_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'due_date': self.due_date,
            'asigned_to': self.asigned_to
        }

    @staticmethod
    def from_dict(data):
        return Task(
            _id=str(data['_id']) if '_id' in data else None,
            task_name=data['task_name'],
            task_description=data.get('task_description'),
            task_status=data.get('task_status', 'initialized'),
            asignee_id=data.get('asignee_id'),
            project_id=str(data.get('project_id')),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            due_date=data.get('due_date'),
            asigned_to=data.get('asigned_to')
        )

