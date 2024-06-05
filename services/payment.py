from database import repository

class PaymentService:
    def __init__(self):
        pass

    def get_worker_payment(self, worker_id):
        tasks = repository.get_tasks_by_worker_id(worker_id)
        total = 0

        for task in tasks:
            if task.status == 'completed':
                total += task.payment

        return total

    def get_preview_maker_payment(self, preview_maker_id):
        previews = repository.get_previews_by_preview_maker_id(preview_maker_id)
        total = 0

        for preview in previews:
            total += preview.payment

        return total

    def get_total_payments(self, channel_id):
        payments = repository.get_payments_by_channel_id(channel_id)
        return sum(payment.amount for payment in payments)