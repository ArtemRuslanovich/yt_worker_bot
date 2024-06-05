from database import repository

class PreviewsService:
    def __init__(self):
        pass

    def create_preview(self, video_id, preview_maker_id, deadline, channel_id):
        preview = repository.create_preview(video_id, preview_maker_id, deadline, channel_id)
        return preview

    def get_preview_by_id(self, preview_id):
        preview = repository.get_preview_by_id(preview_id)
        return preview

    def update_preview(self, preview_id, status, link):
        preview = repository.update_preview(preview_id, status, link)
        return preview

    def get_previews_by_preview_maker_id(self, preview_maker_id):
        previews = repository.get_previews_by_preview_maker_id(preview_maker_id)
        return previews

    def get_previews_by_channel_id(self, channel_id):
        previews = repository.get_previews_by_channel_id(channel_id)
        return previews

    def get_overdue_previews(self):
        previews = repository.get_overdue_previews()
        return previews