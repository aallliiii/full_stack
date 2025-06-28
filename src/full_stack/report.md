import unittest
import datetime
from Finance_manager import finance_manager

class TestFinanceManager(unittest.TestCase):

    def setUp(self):
        """
        Set up a fresh Finance_manager instance before each test.
        """
        self.fm = finance_manager()

    # --- Test Internal Validation and Helper Methods ---

    def test_validate_amount_valid(self):
        self.assertEqual(self.fm._validate_amount(100.55), 100.55)
        self.assertEqual(self.fm._validate_amount(0), 0.0)
        self.assertEqual(self.fm._validate_amount(123), 123.00)
        self.assertEqual(self.fm._validate_amount(99.999), 100.00) # Test rounding

    def test_validate_amount_invalid(self):
        with self.assertRaisesRegex(ValueError, "Amount must be a non-negative number."):
            self.fm._validate_amount(-50)
        with self.assertRaisesRegex(ValueError, "Amount must be a non-negative number."):
            self.fm._validate_amount("abc")
        with self.assertRaisesRegex(ValueError, "Amount must be a non-negative number."):
            self.fm._validate_amount(None)

    def test_parse_date_valid(self):
        self.assertEqual(self.fm._parse_date("2023-01-15"), datetime.date(2023, 1, 15))
        self.assertEqual(self.fm._parse_date("1999-12-31"), datetime.date(1999, 12, 31))

    def test_parse_date_invalid(self):
        with self.assertRaisesRegex(ValueError, "Invalid date format. Please use YYYY-MM-DD."):
            self.fm._parse_date("2023/01/15")
        with self.assertRaisesRegex(ValueError, "Invalid date format. Please use YYYY-MM-DD."):
            self.fm._parse_date("Jan 15, 2023")
        with self.assertRaisesRegex(ValueError, "Invalid date format. Please use YYYY-MM-DD."):
            self.fm._parse_date("2023-1-1") # Month/day without leading zero
        with self.assertRaisesRegex(ValueError, "Invalid date format. Please use YYYY-MM-DD."):
            self.fm._parse_date("not-a-date")

    def test_is_within_range(self):
        start = datetime.date(2023, 1, 1)
        end = datetime.date(2023, 1, 31)

        self.assertTrue(self.fm._is_within_range(datetime.date(2023, 1, 15), start, end))
        self.assertTrue(self.fm._is_within_range(datetime.date(2023, 1, 1), start, end)) # On start
        self.assertTrue(self.fm._is_within_range(datetime.date(2023, 1, 31), start, end)) # On end
        self.assertFalse(self.fm._is_within_range(datetime.date(2022, 12, 31), start, end)) # Before
        self.assertFalse(self.fm._is_within_range(datetime.date(2023, 2, 1), start, end)) # After

    # --- Test Income Records Management ---

    def test_add_income(self):
        self.fm.add_income("2023-01-01", "Salary", 5000.00)
        self.assertEqual(len(self.fm.incomes), 1)
        self.assertEqual(self.fm.incomes[0]['date'], datetime.date(2023, 1, 1))
        self.assertEqual(self.fm.incomes[0]['source'], "Salary")
        self.assertEqual(self.fm.incomes[0]['amount'], 5000.00)

        self.fm.add_income("2023-01-15", "Bonus", 250.556) # Test rounding
        self.assertEqual(len(self.fm.incomes), 2)
        self.assertEqual(self.fm.incomes[1]['amount'], 250.56)

    def test_add_income_invalid_date(self):
        with self.assertRaises(ValueError):
            self.fm.add_income("2023/01/01", "Salary", 5000)

    def test_add_income_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.fm.add_income("2023-01-01", "Salary", -100)
        with self.assertRaises(ValueError):
            self.fm.add_income("2023-01-01", "Salary", "abc")

    def test_get_income_records_all(self):
        self.fm.add_income("2023-01-01", "Salary", 5000)
        self.fm.add_income("2023-01-15", "Freelance", 1000)
        self.fm.add_income("2023-02-01", "Gift", 500)

        records = self.fm.get_income_records()
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['date'], "2023-01-01")
        self.assertEqual(records[2]['date'], "2023-02-01")

    def test_get_income_records_filtered_by_start_date(self):
        self.fm.add_income("2023-01-01", "Salary", 5000)
        self.fm.add_income("2023-01-15", "Freelance", 1000)
        self.fm.add_income("2023-02-01", "Gift", 500)

        records = self.fm.get_income_records(start_date_str="2023-01-15")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-15")
        self.assertEqual(records[1]['date'], "2023-02-01")

    def test_get_income_records_filtered_by_end_date(self):
        self.fm.add_income("2023-01-01", "Salary", 5000)
        self.fm.add_income("2023-01-15", "Freelance", 1000)
        self.fm.add_income("2023-02-01", "Gift", 500)

        records = self.fm.get_income_records(end_date_str="2023-01-15")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-01")
        self.assertEqual(records[1]['date'], "2023-01-15")

    def test_get_income_records_filtered_by_date_range(self):
        self.fm.add_income("2023-01-01", "Salary", 5000)
        self.fm.add_income("2023-01-15", "Freelance", 1000)
        self.fm.add_income("2023-02-01", "Gift", 500)
        self.fm.add_income("2023-02-10", "Investments", 200)

        records = self.fm.get_income_records(start_date_str="2023-01-10", end_date_str="2023-02-05")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-15")
        self.assertEqual(records[1]['date'], "2023-02-01")

    def test_get_income_records_no_records(self):
        records = self.fm.get_income_records()
        self.assertEqual(len(records), 0)

    def test_get_income_records_invalid_date_filter(self):
        self.fm.add_income("2023-01-01", "Salary", 5000)
        with self.assertRaises(ValueError):
            self.fm.get_income_records(start_date_str="invalid-date")
        with self.assertRaises(ValueError):
            self.fm.get_income_records(end_date_str="another-invalid-date")

    # --- Test Expense Records Management ---

    def test_add_expense(self):
        self.fm.add_expense("2023-01-05", "Food", 50.75, "Groceries at market")
        self.assertEqual(len(self.fm.expenses), 1)
        self.assertEqual(self.fm.expenses[0]['date'], datetime.date(2023, 1, 5))
        self.assertEqual(self.fm.expenses[0]['category'], "Food")
        self.assertEqual(self.fm.expenses[0]['amount'], 50.75)
        self.assertEqual(self.fm.expenses[0]['note'], "Groceries at market")

        self.fm.add_expense("2023-01-06", "Transport", 10.00) # Without note
        self.assertEqual(len(self.fm.expenses), 2)
        self.assertEqual(self.fm.expenses[1]['note'], "")

        self.fm.add_expense("2023-01-07", "Utilities", 123.456) # Test rounding
        self.assertEqual(self.fm.expenses[2]['amount'], 123.46)

    def test_add_expense_invalid_date(self):
        with self.assertRaises(ValueError):
            self.fm.add_expense("05-01-2023", "Food", 50)

    def test_add_expense_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.fm.add_expense("2023-01-05", "Food", -10)
        with self.assertRaises(ValueError):
            self.fm.add_expense("2023-01-05", "Food", "fifty")

    def test_get_expense_records_all(self):
        self.fm.add_expense("2023-01-05", "Food", 50)
        self.fm.add_expense("2023-01-10", "Rent", 1000)
        self.fm.add_expense("2023-02-01", "Utilities", 75)

        records = self.fm.get_expense_records()
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['date'], "2023-01-05")
        self.assertEqual(records[2]['date'], "2023-02-01")

    def test_get_expense_records_filtered_by_start_date(self):
        self.fm.add_expense("2023-01-05", "Food", 50)
        self.fm.add_expense("2023-01-10", "Rent", 1000)
        self.fm.add_expense("2023-02-01", "Utilities", 75)

        records = self.fm.get_expense_records(start_date_str="2023-01-10")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-10")
        self.assertEqual(records[1]['date'], "2023-02-01")

    def test_get_expense_records_filtered_by_end_date(self):
        self.fm.add_expense("2023-01-05", "Food", 50)
        self.fm.add_expense("2023-01-10", "Rent", 1000)
        self.fm.add_expense("2023-02-01", "Utilities", 75)

        records = self.fm.get_expense_records(end_date_str="2023-01-10")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-05")
        self.assertEqual(records[1]['date'], "2023-01-10")

    def test_get_expense_records_filtered_by_date_range(self):
        self.fm.add_expense("2023-01-05", "Food", 50)
        self.fm.add_expense("2023-01-10", "Rent", 1000)
        self.fm.add_expense("2023-02-01", "Utilities", 75)
        self.fm.add_expense("2023-02-15", "Entertainment", 120)

        records = self.fm.get_expense_records(start_date_str="2023-01-08", end_date_str="2023-02-05")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['date'], "2023-01-10")
        self.assertEqual(records[1]['date'], "2023-02-01")

    def test_get_expense_records_no_records(self):
        records = self.fm.get_expense_records()
        self.assertEqual(len(records), 0)

    def test_get_expense_records_invalid_date_filter(self):
        self.fm.add_expense("2023-01-01", "Food", 50)
        with self.assertRaises(ValueError):
            self.fm.get_expense_records(start_date_str="invalid-date")
        with self.assertRaises(ValueError):
            self.fm.get_expense_records(end_date_str="another-invalid-date")

    # --- Test Budget Planner ---

    def test_set_budget_new_category(self):
        self.fm.set_budget("Food", 300.00)
        self.assertEqual(self.fm.budgets['food']['monthly_limit'], 300.00)
        self.fm.set_budget("Utilities", 150.50)
        self.assertEqual(self.fm.budgets['utilities']['monthly_limit'], 150.50)

    def test_set_budget_update_category(self):
        self.fm.set_budget("Food", 300.00)
        self.fm.set_budget("Food", 350.00)
        self.assertEqual(self.fm.budgets['food']['monthly_limit'], 350.00)

    def test_set_budget_case_insensitivity(self):
        self.fm.set_budget("FOOD", 300.00)
        self.assertEqual(self.fm.budgets['food']['monthly_limit'], 300.00)
        self.fm.set_budget("food", 350.00)
        self.assertEqual(self.fm.budgets['food']['monthly_limit'], 350.00)

    def test_set_budget_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.fm.set_budget("Rent", -1000)
        with self.assertRaises(ValueError):
            self.fm.set_budget("Rent", "one thousand")

    def test_get_budgets(self):
        self.fm.set_budget("Food", 300)
        self.fm.set_budget("Rent", 1000)
        budgets = self.fm.get_budgets()
        self.assertEqual(budgets, {'food': {'monthly_limit': 300.0}, 'rent': {'monthly_limit': 1000.0}})

    def test_get_budgets_empty(self):
        budgets = self.fm.get_budgets()
        self.assertEqual(budgets, {})

    def test_get_monthly_spending_by_category(self):
        self.fm.add_expense("2023-01-01", "Food", 50)
        self.fm.add_expense("2023-01-10", "Rent", 1000)
        self.fm.add_expense("2023-01-15", "Food", 30)
        self.fm.add_expense("2023-02-01", "Utilities", 75) # Different month
        self.fm.add_expense("2023-01-20", "entertainment", 100) # Test case insensitivity

        spending_jan = self.fm.get_monthly_spending_by_category(2023, 1)
        self.assertEqual(spending_jan, {'food': 80.0, 'rent': 1000.0, 'entertainment': 100.0})

        spending_feb = self.fm.get_monthly_spending_by_category(2023, 2)
        self.assertEqual(spending_feb, {'utilities': 75.0})

        spending_march = self.fm.get_monthly_spending_by_category(2023, 3)
        self.assertEqual(spending_march, {})

    def test_get_budget_status_all_under_budget(self):
        self.fm.set_budget("Food", 300)
        self.fm.set_budget("Utilities", 100)
        self.fm.add_expense("2023-03-01", "Food", 100)
        self.fm.add_expense("2023-03-15", "Utilities", 50)

        status = self.fm.get_budget_status(2023, 3)
        expected_status = [
            {'category': 'Food', 'limit': 300.0, 'spent': 100.0, 'remaining': 200.0, 'alert': False},
            {'category': 'Utilities', 'limit': 100.0, 'spent': 50.0, 'remaining': 50.0, 'alert': False}
        ]
        self.assertEqual(len(status), len(expected_status))
        self.assertCountEqual(status, expected_status) # Use assertCountEqual for list of dicts regardless of order

    def test_get_budget_status_with_alert(self):
        self.fm.set_budget("Food", 100)
        self.fm.set_budget("Transport", 50)
        self.fm.add_expense("2023-03-01", "Food", 90.0) # 90%
        self.fm.add_expense("2023-03-10", "Transport", 40.0) # 80%

        status = self.fm.get_budget_status(2023, 3)
        expected_status = [
            {'category': 'Food', 'limit': 100.0, 'spent': 90.0, 'remaining': 10.0, 'alert': True},
            {'category': 'Transport', 'limit': 50.0, 'spent': 40.0, 'remaining': 10.0, 'alert': False}
        ]
        self.assertEqual(len(status), len(expected_status))
        self.assertCountEqual(status, expected_status)

    def test_get_budget_status_over_budget(self):
        self.fm.set_budget("Food", 100)
        self.fm.add_expense("2023-03-01", "Food", 120)

        status = self.fm.get_budget_status(2023, 3)
        expected_status = [
            {'category': 'Food', 'limit': 100.0, 'spent': 120.0, 'remaining': -20.0, 'alert': True}
        ]
        self.assertEqual(status, expected_status)

    def test_get_budget_status_category_not_budgeted(self):
        self.fm.add_expense("2023-03-01", "Groceries", 75)
        self.fm.add_expense("2023-03-05", "Shopping", 150)

        status = self.fm.get_budget_status(2023, 3)
        expected_status = [
            {'category': 'Groceries', 'limit': 0.0, 'spent': 75.0, 'remaining': -75.0, 'alert': False},
            {'category': 'Shopping', 'limit': 0.0, 'spent': 150.0, 'remaining': -150.0, 'alert': False}
        ]
        self.assertEqual(len(status), len(expected_status))
        self.assertCountEqual(status, expected_status)

    def test_get_budget_status_combined(self):
        self.fm.set_budget("Food", 200)
        self.fm.set_budget("Entertainment", 100)
        self.fm.add_expense("2023-04-01", "Food", 180) # Alert
        self.fm.add_expense("2023-04-05", "Entertainment", 50)
        self.fm.add_expense("2023-04-10", "Shopping", 200) # Not budgeted
        self.fm.add_expense("2023-04-15", "Food", 50) # Now over budget

        status = self.fm.get_budget_status(2023, 4)
        # Total food spent = 180 + 50 = 230
        expected_status = [
            {'category': 'Entertainment', 'limit': 100.0, 'spent': 50.0, 'remaining': 50.0, 'alert': False},
            {'category': 'Food', 'limit': 200.0, 'spent': 230.0, 'remaining': -30.0, 'alert': True},
            {'category': 'Shopping', 'limit': 0.0, 'spent': 200.0, 'remaining': -200.0, 'alert': False}
        ]
        # Sort both lists by category for direct comparison
        status.sort(key=lambda x: x['category'])
        expected_status.sort(key=lambda x: x['category'])
        self.assertEqual(status, expected_status)


    def test_get_budget_status_no_spending(self):
        self.fm.set_budget("Food", 200)
        status = self.fm.get_budget_status(2023, 5)
        expected_status = [
            {'category': 'Food', 'limit': 200.0, 'spent': 0.0, 'remaining': 200.0, 'alert': False}
        ]
        self.assertEqual(status, expected_status)

    def test_get_budget_status_empty(self):
        status = self.fm.get_budget_status(2023, 6)
        self.assertEqual(status, [])

    # --- Test Savings Goals Management ---

    def test_add_savings_goal(self):
        self.fm.add_savings_goal("New Laptop", 1200.00)
        self.assertEqual(self.fm.savings_goals["New Laptop"]["target_amount"], 1200.00)
        self.assertEqual(self.fm.savings_goals["New Laptop"]["amount_saved"], 0.0)
        self.assertEqual(self.fm.savings_goals["New Laptop"]["status"], "In Progress")

        self.fm.add_savings_goal("Vacation Fund", 500.556) # Test rounding
        self.assertEqual(self.fm.savings_goals["Vacation Fund"]["target_amount"], 500.56)


    def test_add_savings_goal_duplicate_name(self):
        self.fm.add_savings_goal("New Laptop", 1200)
        with self.assertRaisesRegex(ValueError, "Savings goal 'New Laptop' already exists."):
            self.fm.add_savings_goal("New Laptop", 1500)

    def test_add_savings_goal_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.fm.add_savings_goal("Dream Car", -5000)
        with self.assertRaises(ValueError):
            self.fm.add_savings_goal("Dream Car", "ten thousand")

    def test_update_savings_progress_partial(self):
        self.fm.add_savings_goal("New Laptop", 1200)
        self.fm.update_savings_progress("New Laptop", 200)
        self.assertEqual(self.fm.savings_goals["New Laptop"]["amount_saved"], 200.0)
        self.assertEqual(self.fm.savings_goals["New Laptop"]["status"], "In Progress")

        self.fm.update_savings_progress("New Laptop", 300.556) # Test rounding
        self.assertEqual(self.fm.savings_goals["New Laptop"]["amount_saved"], 500.56)

    def test_update_savings_progress_achieved(self):
        self.fm.add_savings_goal("Vacation Fund", 500)
        self.fm.update_savings_progress("Vacation Fund", 300)
        self.fm.update_savings_progress("Vacation Fund", 200)
        self.assertEqual(self.fm.savings_goals["Vacation Fund"]["amount_saved"], 500.0)
        self.assertEqual(self.fm.savings_goals["Vacation Fund"]["status"], "Achieved")

    def test_update_savings_progress_exceed_target(self):
        self.fm.add_savings_goal("Vacation Fund", 500)
        self.fm.update_savings_progress("Vacation Fund", 600)
        self.assertEqual(self.fm.savings_goals["Vacation Fund"]["amount_saved"], 500.0) # Should cap at target
        self.assertEqual(self.fm.savings_goals["Vacation Fund"]["status"], "Achieved")

    def test_update_savings_progress_non_existent_goal(self):
        with self.assertRaisesRegex(ValueError, "Savings goal 'NonExistent' not found."):
            self.fm.update_savings_progress("NonExistent", 100)

    def test_update_savings_progress_invalid_amount(self):
        self.fm.add_savings_goal("New Laptop", 1200)
        with self.assertRaises(ValueError):
            self.fm.update_savings_progress("New Laptop", -50)
        with self.assertRaises(ValueError):
            self.fm.update_savings_progress("New Laptop", "one hundred")

    def test_get_savings_goals(self):
        self.fm.add_savings_goal("New Laptop", 1200)
        self.fm.add_savings_goal("Vacation Fund", 500)
        self.fm.update_savings_progress("New Laptop", 300)
        self.fm.update_savings_progress("Vacation Fund", 500)

        goals = self.fm.get_savings_goals()
        self.assertEqual(len(goals), 2)
        # Sort for consistent comparison
        goals.sort(key=lambda x: x['name'])

        expected_goals = [
            {'name': 'New Laptop', 'target_amount': 1200.0, 'amount_saved': 300.0, 'status': 'In Progress'},
            {'name': 'Vacation Fund', 'target_amount': 500.0, 'amount_saved': 500.0, 'status': 'Achieved'}
        ]
        expected_goals.sort(key=lambda x: x['name'])
        self.assertEqual(goals, expected_goals)

    def test_get_savings_goals_empty(self):
        goals = self.fm.get_savings_goals()
        self.assertEqual(goals, [])

    # --- Test Recurring Payments Management ---

    def test_add_recurring_payment(self):
        self.fm.add_recurring_payment("Rent", 1000.00, "Housing", "Monthly")
        self.assertEqual(len(self.fm.recurring_payments), 1)
        self.assertEqual(self.fm.recurring_payments[0]['description'], "Rent")
        self.assertEqual(self.fm.recurring_payments[0]['amount'], 1000.00)
        self.assertEqual(self.fm.recurring_payments[0]['category'], "Housing")
        self.assertEqual(self.fm.recurring_payments[0]['frequency'], "Monthly")

        self.fm.add_recurring_payment("Netflix", 15.999, "Entertainment", "Monthly") # Test rounding
        self.assertEqual(self.fm.recurring_payments[1]['amount'], 16.00)

    def test_add_recurring_payment_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.fm.add_recurring_payment("Gym Membership", -30, "Health", "Monthly")
        with self.assertRaises(ValueError):
            self.fm.add_recurring_payment("Gym Membership", "thirty", "Health", "Monthly")

    def test_get_recurring_payments(self):
        self.fm.add_recurring_payment("Rent", 1000, "Housing", "Monthly")
        self.fm.add_recurring_payment("Spotify", 9.99, "Entertainment", "Monthly")

        payments = self.fm.get_recurring_payments()
        self.assertEqual(len(payments), 2)
        expected_payments = [
            {'description': 'Rent', 'amount': 1000.0, 'category': 'Housing', 'frequency': 'Monthly'},
            {'description': 'Spotify', 'amount': 9.99, 'category': 'Entertainment', 'frequency': 'Monthly'}
        ]
        self.assertEqual(payments, expected_payments)

    def test_get_recurring_payments_empty(self):
        payments = self.fm.get_recurring_payments()
        self.assertEqual(payments, [])

    # --- Test Spending Summary by Category ---

    def test_get_spending_summary_by_category(self):
        self.fm.add_expense("2023-01-01", "Food", 50)
        self.fm.add_expense("2023-01-05", "Transport", 25)
        self.fm.add_expense("2023-01-10", "Food", 30)
        self.fm.add_expense("2023-02-01", "Food", 40) # Outside range
        self.fm.add_expense("2023-01-15", "Entertainment", 50)
        self.fm.add_expense("2023-01-20", "Transport", 15)

        summary = self.fm.get_spending_summary_by_category("2023-01-01", "2023-01-31")
        
        # Total spending: Food (50+30=80) + Transport (25+15=40) + Entertainment (50) = 170
        # Food: 80/170 = 47.06%
        # Transport: 40/170 = 23.53%
        # Entertainment: 50/170 = 29.41%

        expected_summary = [
            {'category': 'Food', 'total_spent': 80.0, 'percentage_of_total': 47.06},
            {'category': 'Entertainment', 'total_spent': 50.0, 'percentage_of_total': 29.41},
            {'category': 'Transport', 'total_spent': 40.0, 'percentage_of_total': 23.53}
        ]
        self.assertEqual(len(summary), len(expected_summary))
        # Need to sort to ensure order is consistent for comparison
        summary.sort(key=lambda x: x['category'])
        expected_summary.sort(key=lambda x: x['category'])
        self.assertEqual(summary, expected_summary)


    def test_get_spending_summary_by_category_no_expenses_in_range(self):
        self.fm.add_expense("2023-01-01", "Food", 50)
        summary = self.fm.get_spending_summary_by_category("2023-02-01", "2023-02-28")
        self.assertEqual(summary, [])

    def test_get_spending_summary_by_category_no_expenses_at_all(self):
        summary = self.fm.get_spending_summary_by_category("2023-01-01", "2023-01-31")
        self.assertEqual(summary, [])

    def test_get_spending_summary_by_category_invalid_date_range(self):
        self.fm.add_expense("2023-01-01", "Food", 50)
        with self.assertRaises(ValueError):
            self.fm.get_spending_summary_by_category("invalid-date", "2023-01-31")
        with self.assertRaises(ValueError):
            self.fm.get_spending_summary_by_category("2023-01-01", "another-invalid-date")

    def test_get_spending_summary_by_category_start_end_same(self):
        self.fm.add_expense("2023-01-15", "Food", 50)
        self.fm.add_expense("2023-01-16", "Transport", 20)
        summary = self.fm.get_spending_summary_by_category("2023-01-15", "2023-01-15")
        self.assertEqual(summary, [{'category': 'Food', 'total_spent': 50.0, 'percentage_of_total': 100.0}])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)