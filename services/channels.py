from database.repository import DatabaseRepository

class ChannelsService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def create_channel(self, name, manager_id, link):
        return self.db_repository.create_channel(name, manager_id, link)

    def get_channel_by_id(self, channel_id):
        return self.db_repository.get_channel_by_id(channel_id)

    def update_channel(self, channel_id, **kwargs):
        return self.db_repository.update_channel(channel_id, **kwargs)

    def delete_channel(self, channel_id):
        return self.db_repository.delete_channel(channel_id)

    def get_channels_by_manager_id(self, manager_id):
        return self.db_repository.get_channels_by_manager_id(manager_id)

    def get_channels_by_worker_id(self, worker_id):
        return self.db_repository.get_channels_by_worker_id(worker_id)

    def get_channels_by_preview_maker_id(self, preview_maker_id):
        return self.db_repository.get_channels_by_preview_maker_id(preview_maker_id)
