from database.repository import DatabaseRepository


class PreviewsService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def get_preview_by_id(self, preview_id):
        return self.db_repository.get_preview_by_id(preview_id)

    def update_preview(self, preview_id, status, link):
        return self.db_repository.update_preview(preview_id, status, link)

    def get_previews_by_preview_maker_id(self, preview_maker_id):
        return self.db_repository.get_previews_by_preview_maker_id(preview_maker_id)

    def get_preview_maker_statistics(self, preview_maker_id):
        previews = self.db_repository.get_previews_by_preview_maker_id(preview_maker_id)
        return len(previews)
