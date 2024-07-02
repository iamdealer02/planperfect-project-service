class Tasks:
    def __init__(self, task_id, task_name, task_description, task_status, asignee_id, project_id, created_at, updated_at, due_date, asigned_to):
        self.task_id = task_id
        self.task_name = task_name
        self.task_description = task_description
        self.task_status = task_status
        self.asignee_id = asignee_id
        self.project_id = project_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.due_date = due_date
        self.asigned_to = asigned_to

    def to_dict(self):
        return {
            'task_id': self.task_id,
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
        return Tasks(
            task_id=data['task_id'],
            task_name=data['task_name'],
            task_description=data['task_description'],
            task_status=data['task_status'],
            asignee_id=data['asignee_id'],
            project_id=data['project_id'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            due_date=data['due_date'],
            asigned_to=data['asigned_to']
        )