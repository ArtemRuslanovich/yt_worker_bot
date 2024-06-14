from aiogram import types

def role_checker(role):
    async def inner_checker(obj):
        if isinstance(obj, types.Message):
            return obj.user.role.name == role
        return False
    return inner_checker

#