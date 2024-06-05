from database import repository

class ChannelsService:
    def __init__(self):
        pass

    def create_channel(self, name, manager_id):
        channel = repository.create_channel(name, manager_id)
        return channel

    def get_channel_by_id(self, channel_id):
        channel = repository.get_channel_by_id(channel_id)
        return channel

    def update_channel(self, channel_id, name):
        channel = repository.update_channel(channel_id, name)
        return channel

    def get_channels_by_manager_id(self, manager_id):
        channels = repository.get_channels_by_manager_id(manager_id)
        return channels

    def get_channels_by_worker_id(self, worker_id):
        channels = repository.get_channels_by_worker_id(worker_id)
        return channels

    def get_channels_by_preview_maker_id(self, preview_maker_id):
        channels = repository.get_channels_by_preview_maker_id(preview_maker_id)
        return channels