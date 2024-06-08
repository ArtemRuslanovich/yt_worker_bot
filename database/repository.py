import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .models import User, Role, Task, Expense, Channel, user_channel_association

class DatabaseRepository:
    def __init__(self, session: Session):
        self.session = session

    # User CRUD operations
    def create_user(self, username, password, role_id):
        user = User(username=username, password=password, role_id=role_id)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_username(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()

    def update_user(self, user_id, **kwargs):
        user = self.get_user_by_id(user_id)
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.session.commit()
        return user

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        self.session.delete(user)
        self.session.commit()

    # Role CRUD operations
    def create_role(self, name):
        role = Role(name=name)
        self.session.add(role)
        self.session.commit()
        return role

    def get_role_by_name(self, name):
        return self.session.query(Role).filter_by(name=name).first()

    def get_role_by_id(self, role_id):
        return self.session.query(Role).filter_by(id=role_id).first()

    def update_role(self, role_id, **kwargs):
        role = self.get_role_by_id(role_id)
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        self.session.commit()
        return role

    def delete_role(self, role_id):
        role = self.get_role_by_id(role_id)
        self.session.delete(role)
        self.session.commit()

    # Task CRUD operations
    def create_task(self, user_id, title, description, deadline, status):
        task = Task(user_id=user_id, title=title, description=description, deadline=deadline, status=status)
        self.session.add(task)
        self.session.commit()
        return task

    def get_task_by_id(self, task_id):
        return self.session.query(Task).filter_by(id=task_id).first()

    def get_tasks_by_user_id(self, user_id):
        return self.session.query(Task).filter_by(user_id=user_id).all()

    def update_task(self, task_id, **kwargs):
        task = self.get_task_by_id(task_id)
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        self.session.commit()
        return task

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        self.session.delete(task)
        self.session.commit()

    # Expense CRUD operations
    def create_expense(self, user_id, amount, currency):
        expense = Expense(user_id=user_id, amount=amount, currency=currency)
        self.session.add(expense)
        self.session.commit()
        return expense

    def get_expense_by_id(self, expense_id):
        return self.session.query(Expense).filter_by(id=expense_id).first()

    def get_expenses_by_user_id(self, user_id):
        return self.session.query(Expense).filter_by(user_id=user_id).all()

    def update_expense(self, expense_id, **kwargs):
        expense = self.get_expense_by_id(expense_id)
        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        self.session.commit()
        return expense

    def delete_expense(self, expense_id):
        expense = self.get_expense_by_id(expense_id)
        self.session.delete(expense)
        self.session.commit()
        
    def get_overdue_tasks(self):
        return self.session.query(Task).filter(Task.deadline < datetime.datetime.now()).all()
    
    def get_user_role(user_id: int) -> str:
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).one_or_none()
            if user:
                return user.role
            else:
                return 'unknown'
    
    # Channel CRUD operations
    def create_channel(self, name, manager_id, link):
        channel = Channel(name=name, link=link, manager_id=manager_id)
        self.session.add(channel)
        self.session.commit()
        return channel

    def get_channel_by_id(self, channel_id):
        return self.session.query(Channel).filter_by(id=channel_id).first()

    def update_channel(self, channel_id, name):
        channel = self.get_channel_by_id(channel_id)
        channel.name = name
        self.session.commit()
        return channel

    def get_channels_by_manager_id(self, manager_id):
        return self.session.query(Channel).filter_by(manager_id=manager_id).all()

    def get_channels_by_worker_id(self, worker_id):
        return self.session.query(Channel).join(user_channel_association).filter(user_channel_association.c.user_id == worker_id).all()
    
    def get_channels_by_preview_maker_id(self, preview_maker_id):
        return self.session.query(Channel).join(user_channel_association).filter(user_channel_association.c.user_id == preview_maker_id).all()
