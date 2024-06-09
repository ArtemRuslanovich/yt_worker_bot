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
    channels = relationship('Channel', secondary=user_channel_association, back_populates='workers')

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    deadline = Column(DateTime)
    status = Column(String, default='pending')

    user = relationship('User', back_populates='tasks')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    currency = Column(String)
    channel_id = Column(Integer, ForeignKey('channels.id'))

    user = relationship('User', back_populates='expenses')
    channel = relationship('Channel', back_populates='expenses')

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

    manager = relationship('User', back_populates='managed_channels')
    workers = relationship('User', secondary=user_channel_association, back_populates='channels')
    payments = relationship('Payment', back_populates='channel')
    expenses = relationship('Expense', back_populates='channel')

    @property
    def total_expenses(self):
        return sum(expense.amount for expense in self.expenses)

    @property
    def total_payments(self):
        return sum(payment.amount for payment in self.payments)
    

class Preview(Base):
    __tablename__ = 'previews'

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'))
    preview_maker_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String)
    link = Column(String)
    payment = Column(Float)

    video = relationship('Video')
    preview_maker = relationship('User', backref='previews')