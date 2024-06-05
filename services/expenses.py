from database import repository

class ExpensesService:
    def __init__(self):
        pass

    def log_expense(self, user_id, amount, currency):
        expense = repository.create_expense(user_id, amount, currency)
        return expense

    def get_total_expenses(self, channel_id):
        expenses = repository.get_expenses_by_channel_id(channel_id)
        total_usd = 0
        total_rub = 0

        for expense in expenses:
            if expense.currency == 'USD':
                total_usd += expense.amount
            elif expense.currency == 'RUB':
                total_rub += expense.amount

        return total_usd, total_rub