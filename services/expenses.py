from database.repository import DatabaseRepository


class ExpensesService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def log_expense(self, user_id, amount, currency, channel_id):
        return self.db_repository.create_expense(user_id, amount, currency, channel_id)

    def get_total_expenses(self, channel_id):
        expenses = self.db_repository.get_expenses_by_channel_id(channel_id)
        total_usd = 0
        total_rub = 0
#
        for expense in expenses:
            if expense.currency == 'USD':
                total_usd += expense.amount
            elif expense.currency == 'RUB':
                total_rub += expense.amount

        return total_usd, total_rub
