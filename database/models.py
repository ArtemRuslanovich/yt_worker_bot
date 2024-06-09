from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

user_channel_association = Table(
    'user_channel_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    username = Column(String, unique=True)
    password = Column(String)

    role = relationship('Role')

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    title = Column(String)
    theme = Column(String, nullable=True)  # Добавлено для хранения темы задачи
    description = Column(String)
    deadline = Column(DateTime)
    status = Column(String)
    link = Column(String)
    actual_completion_date = Column(DateTime)

    user = relationship('User')
    channel = relationship('Channel')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    amount = Column(Float)
    currency = Column(String)

    user = relationship('User')
    channel = relationship('Channel')

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    amount = Column(Float)

    channel = relationship('Channel', back_populates='payments')

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    link = Column(String)
    manager_id = Column(Integer, ForeignKey('users.id'))

    manager = relationship('User', backref='managed_channels')
    workers = relationship('User', secondary=user_channel_association, backref='channels')
    payments = relationship('Payment', back_populates='channel')

    @property
    def total_expenses(self):
        return sum(expense.amount for expense in self.expenses)

    @property
    def total_payments(self):
        return sum(payment.amount for payment in self.payments)

class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    upload_date = Column(DateTime)
    worker_id = Column(Integer, ForeignKey('users.id'))

    worker = relationship('User')

class Preview(Base):
    __tablename__ = 'previews'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'))
    preview_maker_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String)
    link = Column(String)
    payment = Column(Float)
    technical_description = Column(String, nullable=True)  # Добавлено для хранения ТЗ

    video = relationship('Video')
    preview_maker = relationship('User')
