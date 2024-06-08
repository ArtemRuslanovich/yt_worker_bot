from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Table
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
    username = Column(String)
    password = Column(String)

    role = relationship('Role')
    managed_channels = relationship('Channel', back_populates='manager')
    channels = relationship('Channel', secondary=user_channel_association, back_populates='users')

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    description = Column(String)
    deadline = Column(DateTime)
    status = Column(String)

    user = relationship('User')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)
    currency = Column(String)

    user = relationship('User')

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    manager_id = Column(Integer, ForeignKey('users.id'))

    manager = relationship('User', back_populates='managed_channels')
    users = relationship('User', secondary=user_channel_association, back_populates='channels')
