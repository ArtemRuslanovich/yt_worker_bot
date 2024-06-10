import datetime
from sqlalchemy.orm import Session
from .models import Payment, Preview, User, Role, Task, Expense, Channel, Video

class DatabaseRepository:
    def __init__(self, session: Session):
        self.session = session

    # CRUD операции для моделей, таких как User, Role, Task, Expense, Channel, Video, Preview
    def create_item(self, model, **kwargs):
        item = model(**kwargs)
        self.session.add(item)
        self.session.commit()
        return item

    def get_item_by_id(self, model, item_id):
        return self.session.query(model).filter_by(id=item_id).first()

    def update_item(self, model, item_id, **kwargs):
        item = self.get_item_by_id(model, item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.session.commit()
        return item

    def delete_item(self, model, item_id):
        item = self.get_item_by_id(model, item_id)
        if item:
            self.session.delete(item)
            self.session.commit()

    # Специфические запросы и операции
    def get_items_by_attribute(self, model, **kwargs):
        return self.session.query(model).filter_by(**kwargs).all()

    def get_overdue_tasks(self):
        return self.session.query(Task).filter(Task.deadline < datetime.datetime.now()).all()

    def get_user_role(self, user_id):
        user = self.get_item_by_id(User, user_id)
        return user.role.name if user else 'unknown'

    def calculate_total(self, model, channel_id):
        items = self.session.query(model).filter_by(channel_id=channel_id).all()
        return sum(item.amount for item in items)

    def get_items_by_month(self, model, month):
        start_date = datetime.datetime(datetime.datetime.now().year, month, 1)
        end_date = datetime.datetime(datetime.datetime.now().year, month + 1, 1) if month < 12 else datetime.datetime(datetime.datetime.now().year + 1, 1, 1)
        return self.session.query(model).filter(model.upload_date >= start_date, model.upload_date < end_date).all()

    def set_worker_salary(self, worker_id, salary):
        worker = self.get_item_by_id(User, worker_id)
        if worker:
            worker.salary = salary
            self.session.commit()
            return True
        return False
    
    def get_all_channels(self):
        return self.session.query(Channel).all()

    def get_all_users_by_role(self, role_name):
        return self.session.query(User).join(Role).filter(Role.name == role_name).all()
    
    def get_item_by_id(self, model, item_id):
        return self.session.query(model).filter_by(id=item_id).first()

    def get_user_by_username(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def get_channel_by_name(self, name):
        return self.session.query(Channel).filter_by(name=name).first()

    def create_channel(self, name):
        new_channel = Channel(name=name)
        self.session.add(new_channel)
        self.session.commit()
        return new_channel

    def get_all_channels(self):
        return self.session.query(Channel).all()

    def get_all_users_by_role(self, role_name):
        return self.session.query(User).join(Role).filter(Role.name == role_name).all()
    def get_item_by_id(self, model, item_id):
        return self.session.query(model).filter_by(id=item_id).first()

    def get_user_by_username(self, username):
        return self.session.query(User).filter_by(username=username).first()

    def get_channel_by_name(self, name):
        return self.session.query(Channel).filter_by(name=name).first()

    def create_channel(self, name):
        new_channel = Channel(name=name)
        self.session.add(new_channel)
        self.session.commit()
        return new_channel

    def get_all_channels(self):
        return self.session.query(Channel).all()

    def get_all_users_by_role(self, role_name):
        return self.session.query(User).join(Role).filter(Role.name == role_name).all()