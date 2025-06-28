

The error indicates a `SyntaxError: '(' was never closed` on line 713 (in the context of the provided code, this line refers to `membership = Membership("Monthly", self.today`). This suggests a typo or incomplete line in the test code itself, not necessarily an issue with the mocking strategy. I need to fix this syntax error.

Looking at the line again:
`membership = Membership("Monthly", self.today`

It's missing the `end_date` and `fee` arguments, and the closing parenthesis. This appears in `TestMembership.test_membership_initialization`. I had fixed it previously for another test, but perhaps not everywhere.

I also need to be careful with the `self.mock_uuid_instance.side_effect = uuid_hex_generator()` as it modifies the global `uuid.uuid4()` for all subsequent tests, which might cause issues if a test relies on specific UUIDs generated in a certain order. The current implementation relies on a sequential generator, which is generally good, but I must ensure the test order (or number of UUIDs consumed) doesn't break assumptions.

Let's carefully correct `TestMembership.test_membership_initialization` and ensure all `Membership` instantiations are complete.

It seems the current Code Interpreter environment doesn't retain the previous context, meaning I have to provide the *entire* corrected file again.

I'll also double-check the `side_effect` for `mock_uuid_instance` across all tests to ensure the sequence of UUIDs is handled gracefully. The generator approach is robust against running out of UUIDs, but specific tests might depend on specific mock UUIDs being generated. I should ensure that any test that `assertEqual` on a specific mock UUID ('mock_uuid_001', etc.) is expecting the correct number in the sequence. For example, `test_create_member` asserts `member_id == 'mock_uuid_001'` and `member_id_2 == 'mock_uuid_002'`, which implies two `uuid.uuid4()` calls. Then if `test_purchase_membership_success` runs next, it will start consuming from `mock_uuid_003`. This is acceptable with a sequential generator.

The main issue is the `SyntaxError`. I need to fix:

`membership = Membership("Monthly", self.today`
to
`membership = Membership("Monthly", self.today, self.future_date, 30.00)`

Let's re-generate the full test file with this fix.```python
import unittest
import datetime
from unittest.mock import patch, MagicMock
import uuid

# The content of accounts.py should be in the same directory and imported normally.
# For the purpose of this self-contained response, I'm including the module's code directly.
# In a real scenario, you would use:
# from accounts import get_membership_fee, Member, Membership, FitnessClass, Payment, Account

# --- accounts.py content (for standalone test file execution) ---

def get_membership_fee(plan_name: str) -> float:
    """
    Helper function: Returns the current price for a membership plan.
    This is a test implementation.

    Args:
        plan_name (str): The name of the membership plan (e.g., "Monthly", "Quarterly", "Annual").

    Returns:
        float: The associated fee for the plan, or 0.0 if the plan is unknown.
    """
    fees = {
        "Monthly": 30.00,
        "Quarterly": 80.00,
        "Annual": 300.00,
    }
    return fees.get(plan_name, 0.0)

class Member:
    """Represents a member of the fitness club."""
    def __init__(self, member_id: str, name: str, contact_info: str):
        """
        Initializes a new Member instance.
        Args:
            member_id (str): A unique identifier for the member.
            name (str): The member's full name.
            contact_info (str): Contact details (e.g., email address, phone number).
        """
        self.member_id = member_id
        self.name = name
        self.contact_info = contact_info

    def to_dict(self) -> dict:
        """
        Converts the Member object to a dictionary representation.
        Returns:
            Dict: A dictionary containing the member's details.
        """
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact_info": self.contact_info
        }

class Membership:
    """Represents a member's purchased membership plan."""
    def __init__(self, plan_name: str, start_date: datetime.date, end_date: datetime.date, fee: float):
        """
        Initializes a new Membership instance.
        Args:
            plan_name (str): The name of the membership plan (e.g., "Monthly", "Annual").
            start_date (datetime.date): The date the membership starts.
            end_date (datetime.date): The date the membership ends.
            fee (float): The fee paid for the membership.
        """
        self.plan_name = plan_name
        self.start_date = start_date
        self.end_date = end_date
        self.fee = fee

    def is_active(self, as_of_date: datetime.date = None) -> bool:
        """
        Checks if the membership is active on a given date.
        Args:
            as_of_date (Optional[datetime.date]): The date to check against. Defaults to today's date.
        Returns:
            bool: True if the membership is active, False otherwise.
        """
        if as_of_date is None:
            as_of_date = datetime.date.today()
        return self.start_date <= as_of_date <= self.end_date

    def remaining_days(self, as_of_date: datetime.date = None) -> int:
        """
        Calculates remaining days on the active plan.
        Args:
            as_of_date (Optional[datetime.date]): The date to calculate from. Defaults to today's date.
        Returns:
            int: The number of remaining days, or 0 if the membership is not active.
        """
        if not self.is_active(as_of_date):
            return 0
        if as_of_date is None:
            as_of_date = datetime.date.today()
        return (self.end_date - as_of_date).days

    def to_dict(self) -> dict:
        """
        Converts the Membership object to a dictionary representation.
        Returns:
            Dict: A dictionary containing the membership's details.
        """
        return {
            "plan_name": self.plan_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "fee": self.fee,
            "is_active": self.is_active()
        }

class FitnessClass:
    """Represents a fitness class offered by the club."""
    def __init__(self, class_id: str, name: str, start_datetime: datetime.datetime, end_datetime: datetime.datetime, capacity: int):
        """
        Initializes a new FitnessClass instance.
        Args:
            class_id (str): A unique identifier for the class.
            name (str): The name of the class (e.g., "Yoga", "Zumba").
            start_datetime (datetime.datetime): The exact start date and time of the class.
            end_datetime (datetime.datetime): The exact end date and time of the class.
            capacity (int): The maximum number of members allowed in the class.
        """
        self.class_id = class_id
        self.name = name
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.capacity = capacity
        self.enrolled_members: list[str] = []  # List of member_ids currently enrolled
        self.attended_members: list[str] = []  # List of member_ids who attended

    def is_full(self) -> bool:
        """
        Checks if the class has reached its capacity.
        Returns:
            bool: True if the class is full, False otherwise.
        """
        return len(self.enrolled_members) >= self.capacity

    def is_ongoing_or_past(self, current_datetime: datetime.datetime = None) -> bool:
        """
        Checks if the class has already started or is currently ongoing.
        Args:
            current_datetime (Optional[datetime.datetime]): The current time to check against. Defaults to now.
        Returns:
            bool: True if the class has started or passed, False otherwise.
        """
        if current_datetime is None:
            current_datetime = datetime.datetime.now()
        return current_datetime >= self.start_datetime

    def overlaps_with(self, other_class: 'FitnessClass') -> bool:
        """
        Checks if this class's schedule overlaps with another class's schedule.
        Args:
            other_class (FitnessClass): The other class to check for overlap.
        Returns:
            bool: True if there is an overlap, False otherwise.
        """
        return (self.start_datetime < other_class.end_datetime and
                self.end_datetime > other_class.start_datetime)

    def to_dict(self, include_members: bool = False) -> dict:
        """
        Converts the FitnessClass object to a dictionary representation.
        Args:
            include_members (bool): If True, includes enrolled_members and attended_members lists.
        Returns:
            Dict: A dictionary containing the class details.
        """
        data = {
            "class_id": self.class_id,
            "name": self.name,
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": self.end_datetime.isoformat(),
            "capacity": self.capacity,
            "enrolled_count": len(self.enrolled_members),
            "is_full": self.is_full()
        }
        if include_members:
            data["enrolled_members"] = self.enrolled_members
            data["attended_members"] = self.attended_members
        return data

class Payment:
    """Represents a payment made by a member."""
    def __init__(self, payment_id: str, member_id: str, amount: float, date: datetime.datetime, method: str, description: str):
        """
        Initializes a new Payment instance.
        Args:
            payment_id (str): A unique identifier for the payment.
            member_id (str): The ID of the member who made the payment.
            amount (float): The amount of the payment.
            date (datetime.datetime): The date and time the payment was made.
            method (str): The method of payment (e.g., "Credit Card", "Cash").
            description (str): A brief description of the payment (e.g., "Monthly Membership").
        """
        self.payment_id = payment_id
        self.member_id = member_id
        self.amount = amount
        self.date = date
        self.method = method
        self.description = description

    def to_dict(self) -> dict:
        """
        Converts the Payment object to a dictionary representation.
        Returns:
            Dict: A dictionary containing the payment details.
        """
        return {
            "payment_id": self.payment_id,
            "member_id": self.member_id,
            "amount": self.amount,
            "date": self.date.isoformat(),
            "method": self.method,
            "description": self.description
        }

class Account:
    """
    Main class for the Gym Management System.
    Manages members, memberships, classes, and payments.
    """
    def __init__(self):
        """
        Initializes the Gym Management System with empty data stores.
        _members: Stores Member objects, keyed by member_id.
        _memberships: Stores lists of Membership objects for each member, keyed by member_id.
        _classes: Stores FitnessClass objects, keyed by class_id.
        _payments: Stores all Payment objects.
        """
        self._members: dict[str, Member] = {}
        self._memberships: dict[str, list[Membership]] = {}
        self._classes: dict[str, FitnessClass] = {}
        self._payments: list[Payment] = []

    # --- Member Management Methods ---

    def create_member(self, name: str, contact_info: str) -> str:
        """
        Creates a new member account and adds it to the system.

        Args:
            name (str): The full name of the member.
            contact_info (str): The contact information (e.g., email, phone number).

        Returns:
            str: The unique member ID generated for the new member.
        """
        member_id = str(uuid.uuid4())
        new_member = Member(member_id, name, contact_info)
        self._members[member_id] = new_member
        self._memberships[member_id] = []  # Initialize empty list for memberships
        return member_id

    def get_member_details(self, member_id: str) -> dict or None:
        """
        Retrieves details for a specific member.

        Args:
            member_id (str): The unique ID of the member.

        Returns:
            Optional[Dict]: A dictionary of member details if found, otherwise None.
        """
        member = self._members.get(member_id)
        return member.to_dict() if member else None

    def get_all_members_details(self) -> list[dict]:
        """
        Retrieves details for all registered members.

        Returns:
            List[Dict]: A list of dictionaries, each representing a member.
        """
        return [member.to_dict() for member in self._members.values()]

    # --- Membership Management Methods ---

    def _get_current_membership(self, member_id: str, as_of_date: datetime.date = None) -> Membership or None:
        """
        Internal helper: Gets the currently active membership for a member.
        For simplicity, this assumes a member should ideally have only one active membership.
        If multiple exist, it returns the one with the latest end date.

        Args:
            member_id (str): The unique ID of the member.
            as_of_date (Optional[datetime.date]): The date to check for active membership. Defaults to today.

        Returns:
            Optional[Membership]: The active Membership object if found, otherwise None.
        """
        if member_id not in self._memberships or not self._memberships[member_id]:
            return None

        active_memberships = [
            m for m in self._memberships[member_id]
            if m.is_active(as_of_date if as_of_date is not None else datetime.date.today())
        ]
        
        if active_memberships:
            # Return the latest one by end date if multiple are active
            return max(active_memberships, key=lambda m: m.end_date)
        return None

    def purchase_membership(self, member_id: str, plan_name: str, payment_method: str) -> bool:
        """
        Allows a member to purchase a membership plan.

        Args:
            member_id (str): The unique ID of the member.
            plan_name (str): The name of the membership plan (e.g., "Monthly", "Quarterly", "Annual").
            payment_method (str): The method of payment (e.g., "Credit Card", "Cash").

        Returns:
            bool: True if membership was successfully purchased, False otherwise.
        """
        if member_id not in self._members:
            print(f"Error: Member with ID {member_id} not found.")
            return False

        fee = get_membership_fee(plan_name)
        if fee <= 0:
            print(f"Error: Invalid or unknown membership plan '{plan_name}'.")
            return False

        today = datetime.date.today()
        end_date = today
        if plan_name == "Monthly":
            end_date += datetime.timedelta(days=30)
        elif plan_name == "Quarterly":
            end_date += datetime.timedelta(days=90)
        elif plan_name == "Annual":
            end_date += datetime.timedelta(days=365)
        else:
            print(f"Error: Unsupported plan name '{plan_name}'.")
            return False

        new_membership = Membership(plan_name, today, end_date, fee)
        self._memberships[member_id].append(new_membership)

        # Record payment for the membership purchase
        self.record_payment(member_id, fee, datetime.datetime.now(), payment_method,
                            f"{plan_name} Membership Purchase")
        return True

    def is_membership_active(self, member_id: str) -> bool:
        """
        Checks if a member has an active membership.

        Args:
            member_id (str): The unique ID of the member.

        Returns:
            bool: True if the member has an active membership, False otherwise.
        """
        current_membership = self._get_current_membership(member_id)
        return current_membership is not None and current_membership.is_active()

    def get_membership_remaining_days(self, member_id: str) -> int:
        """
        Calculates the remaining days on a member's active plan.

        Args:
            member_id (str): The unique ID of the member.

        Returns:
            int: The number of remaining days, or 0 if no active membership.
        """
        current_membership = self._get_current_membership(member_id)
        if current_membership:
            return current_membership.remaining_days()
        return 0

    # --- Fitness Class Management Methods ---

    def add_class(self, name: str, start_datetime: datetime.datetime, duration_minutes: int, capacity: int) -> str:
        """
        Adds a new fitness class to the system.

        Args:
            name (str): The name of the class.
            start_datetime (datetime.datetime): The exact start date and time of the class.
            duration_minutes (int): The duration of the class in minutes.
            capacity (int): The maximum number of members who can enroll.

        Returns:
            str: The unique class ID generated for the new class.
        """
        class_id = str(uuid.uuid4())
        end_datetime = start_datetime + datetime.timedelta(minutes=duration_minutes)
        new_class = FitnessClass(class_id, name, start_datetime, end_datetime, capacity)
        self._classes[class_id] = new_class
        return class_id

    def enroll_in_class(self, member_id: str, class_id: str) -> bool:
        """
        Enrolls a member in a fitness class, enforcing business rules:
        - Member must exist.
        - Class must exist.
        - Member must have an active membership.
        - Class must not be full.
        - Member must not already be enrolled in this class.
        - Member must not have overlapping class enrollments.

        Args:
            member_id (str): The ID of the member.
            class_id (str): The ID of the class.

        Returns:
            bool: True if enrollment was successful, False otherwise.
        """
        member = self._members.get(member_id)
        fitness_class = self._classes.get(class_id)

        if not member:
            print(f"Enrollment Error: Member {member_id} not found.")
            return False
        if not fitness_class:
            print(f"Enrollment Error: Class {class_id} not found.")
            return False
        if not self.is_membership_active(member_id):
            print(f"Enrollment Error: Member {member_id} does not have an active membership.")
            return False
        if fitness_class.is_full():
            print(f"Enrollment Error: Class '{fitness_class.name}' is full.")
            return False
        if member_id in fitness_class.enrolled_members:
            print(f"Enrollment Error: Member {member_id} already enrolled in '{fitness_class.name}'.")
            return False
        
        # Business Rule: Check for overlapping classes
        member_schedule_class_ids = self.get_member_class_schedule(member_id, return_ids_only=True)
        for enrolled_class_id in member_schedule_class_ids:
            enrolled_class = self._classes.get(enrolled_class_id)
            if enrolled_class and fitness_class.overlaps_with(enrolled_class):
                print(f"Enrollment Error: Member {member_id} has an overlapping class "
                      f"'{enrolled_class.name}' ({enrolled_class.start_datetime.strftime('%Y-%m-%d %H:%M')}).")
                return False

        fitness_class.enrolled_members.append(member_id)
        print(f"Member {member_id} successfully enrolled in '{fitness_class.name}'.")
        return True

    def cancel_class_enrollment(self, member_id: str, class_id: str) -> bool:
        """
        Cancels a member's enrollment in a fitness class, enforcing business rules:
        - Member must exist and be enrolled in the class.
        - Class must exist.
        - Cancellation is not allowed if the class has already started.

        Args:
            member_id (str): The ID of the member.
            class_id (str): The ID of the class.

        Returns:
            bool: True if cancellation was successful, False otherwise.
        """
        fitness_class = self._classes.get(class_id)
        if not fitness_class:
            print(f"Cancellation Error: Class {class_id} not found.")
            return False
        if member_id not in fitness_class.enrolled_members:
            print(f"Cancellation Error: Member {member_id} not enrolled in class '{fitness_class.name}'.")
            return False
        if fitness_class.is_ongoing_or_past():
            print(f"Cancellation Error: Cannot cancel attendance, class '{fitness_class.name}' has already started or passed.")
            return False

        fitness_class.enrolled_members.remove(member_id)
        print(f"Member {member_id} successfully cancelled enrollment from '{fitness_class.name}'.")
        return True

    def record_class_attendance(self, class_id: str, member_ids_present: list[str]) -> dict[str, bool]:
        """
        Records attendance for a fitness class.
        Members must be enrolled to be marked present.

        Args:
            class_id (str): The ID of the class.
            member_ids_present (List[str]): A list of member IDs who were present.

        Returns:
            Dict[str, bool]: A dictionary mapping member_id to True (success) or False (failure for that member).
        """
        fitness_class = self._classes.get(class_id)
        if not fitness_class:
            print(f"Attendance Error: Class {class_id} not found.")
            return {mid: False for mid in member_ids_present}

        results = {}
        for member_id in member_ids_present:
            if member_id in fitness_class.enrolled_members and member_id not in fitness_class.attended_members:
                fitness_class.attended_members.append(member_id)
                results[member_id] = True
            else:
                print(f"Attendance Warning: Member {member_id} not enrolled or already marked present for class '{fitness_class.name}'.")
                results[member_id] = False
        return results

    # --- Payment & Revenue Management Methods ---

    def record_payment(self, member_id: str, amount: float, date: datetime.datetime, method: str, description: str) -> str:
        """
        Records a payment made by a member.

        Args:
            member_id (str): The ID of the member making the payment.
            amount (float): The amount of the payment.
            date (datetime.datetime): The date and time of the payment.
            method (str): The payment method (e.g., "Credit Card", "Cash").
            description (str): A description of the payment (e.g., "Monthly Membership Fee").

        Returns:
            str: The unique payment ID generated for the payment. Returns an empty string if member not found.
        """
        if member_id not in self._members:
            print(f"Payment Error: Member {member_id} not found.")
            return ""
        
        payment_id = str(uuid.uuid4())
        new_payment = Payment(payment_id, member_id, amount, date, method, description)
        self._payments.append(new_payment)
        return payment_id

    def get_total_revenue(self) -> float:
        """
        Calculates the total revenue collected from all members across all payments.

        Returns:
            float: The total revenue.
        """
        return sum(payment.amount for payment in self._payments)

    # --- Reporting Methods ---

    def get_member_class_schedule(self, member_id: str, return_ids_only: bool = False) -> list[dict]:
        """
        Reports a member's current class schedule (classes they are enrolled in).

        Args:
            member_id (str): The ID of the member.
            return_ids_only (bool): If True, returns only a list of class IDs.
                                     Otherwise, returns a list of dictionaries with class details.

        Returns:
            List[Dict] or List[str]: A list of dictionaries with class details,
                                     or a list of class IDs if return_ids_only is True.
                                     Returns an empty list if member not found.
        """
        schedule = []
        if member_id not in self._members:
            return schedule

        for class_id, fitness_class in self._classes.items():
            if member_id in fitness_class.enrolled_members:
                if return_ids_only:
                    schedule.append(class_id)
                else:
                    schedule.append(fitness_class.to_dict())
        return schedule

    def get_member_attendance_history(self, member_id: str) -> list[dict]:
        """
        Reports a member's attendance history for classes they were enrolled in or attended.

        Args:
            member_id (str): The ID of the member.

        Returns:
            List[Dict]: A list of dictionaries with class details and an 'attended' status (True/False).
                        Returns an empty list if member not found.
        """
        attendance_history = []
        if member_id not in self._members:
            return attendance_history

        for fitness_class in self._classes.values():
            if member_id in fitness_class.attended_members:
                class_info = fitness_class.to_dict()
                class_info["attended"] = True
                attendance_history.append(class_info)
            elif member_id in fitness_class.enrolled_members and fitness_class.is_ongoing_or_past():
                # If enrolled but not attended, and class has passed
                class_info = fitness_class.to_dict()
                class_info["attended"] = False
                attendance_history.append(class_info)
        return attendance_history

    def get_member_transactions(self, member_id: str) -> list[dict]:
        """
        Lists all transactions (payments) made by a specific member over time.

        Args:
            member_id (str): The ID of the member.

        Returns:
            List[Dict]: A list of dictionaries with payment details.
                        Returns an empty list if member not found.
        """
        transactions = []
        if member_id not in self._members:
            return transactions
            
        for payment in self._payments:
            if payment.member_id == member_id:
                transactions.append(payment.to_dict())
        return transactions

    def list_available_classes(self) -> list[dict]:
        """
        Lists all classes currently offered by the club, with capacity information.

        Returns:
            List[Dict]: A list of dictionaries, each representing a class with its enrollment and remaining capacity.
        """
        available_classes = []
        for fitness_class in self._classes.values():
            class_info = fitness_class.to_dict()
            class_info["remaining_capacity"] = fitness_class.capacity - len(fitness_class.enrolled_members)
            available_classes.append(class_info)
        return available_classes

# --- End accounts.py content ---


class TestGetMembershipFee(unittest.TestCase):
    def test_known_plans(self):
        self.assertEqual(get_membership_fee("Monthly"), 30.00)
        self.assertEqual(get_membership_fee("Quarterly"), 80.00)
        self.assertEqual(get_membership_fee("Annual"), 300.00)

    def test_unknown_plan(self):
        self.assertEqual(get_membership_fee("Weekly"), 0.0)
        self.assertEqual(get_membership_fee("InvalidPlan"), 0.0)

    def test_case_sensitivity(self):
        self.assertEqual(get_membership_fee("monthly"), 0.0) # Should be case-sensitive per current implementation

class TestMember(unittest.TestCase):
    def test_member_initialization(self):
        member = Member("m1", "John Doe", "john@example.com")
        self.assertEqual(member.member_id, "m1")
        self.assertEqual(member.name, "John Doe")
        self.assertEqual(member.contact_info, "john@example.com")

    def test_to_dict(self):
        member = Member("m2", "Jane Smith", "jane@example.com")
        expected_dict = {"member_id": "m2", "name": "Jane Smith", "contact_info": "jane@example.com"}
        self.assertDictEqual(member.to_dict(), expected_dict)

class TestMembership(unittest.TestCase):
    def setUp(self):
        self.today = datetime.date(2023, 1, 15)
        self.tomorrow = datetime.date(2023, 1, 16)
        self.past_date = datetime.date(2023, 1, 1)
        self.future_date = datetime.date(2023, 2, 15)

    def test_membership_initialization(self):
        # Fix: Ensure all arguments are provided for Membership constructor
        membership = Membership("Monthly", self.today, self.future_date, 30.00)
        self.assertEqual(membership.plan_name, "Monthly")
        self.assertEqual(membership.start_date, self.today)
        self.assertEqual(membership.end_date, self.future_date)
        self.assertEqual(membership.fee, 30.00)

    @patch('datetime.date')
    def test_is_active(self, mock_date):
        mock_date.today.return_value = self.today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
        
        # Active membership
        active_membership = Membership("Monthly", self.past_date, self.future_date, 30.00)
        self.assertTrue(active_membership.is_active(self.today))
        self.assertTrue(active_membership.is_active(self.past_date))
        self.assertTrue(active_membership.is_active(self.future_date))
        self.assertTrue(active_membership.is_active()) # Test with default today

        # Inactive (future) membership
        future_membership = Membership("Monthly", self.future_date, self.future_date + datetime.timedelta(days=30), 30.00)
        self.assertFalse(future_membership.is_active(self.today))

        # Inactive (past) membership
        past_membership = Membership("Monthly", self.past_date - datetime.timedelta(days=30), self.past_date - datetime.timedelta(days=1), 30.00)
        self.assertFalse(past_membership.is_active(self.today))

    @patch('datetime.date')
    def test_remaining_days(self, mock_date):
        mock_date.today.return_value = self.today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
        
        # Membership active and ending in 30 days from today
        membership = Membership("Monthly", self.today, self.today + datetime.timedelta(days=30), 30.00)
        self.assertEqual(membership.remaining_days(self.today), 30)
        self.assertEqual(membership.remaining_days(), 30) # Test with default today
        self.assertEqual(membership.remaining_days(self.today + datetime.timedelta(days=15)), 15)
        self.assertEqual(membership.remaining_days(self.today + datetime.timedelta(days=30)), 0)

        # Membership expired
        expired_membership = Membership("Monthly", self.past_date - datetime.timedelta(days=30), self.past_date, 30.00)
        self.assertEqual(expired_membership.remaining_days(self.today), 0)
        self.assertEqual(expired_membership.remaining_days(), 0)

        # Membership not started yet
        future_membership = Membership("Monthly", self.future_date, self.future_date + datetime.timedelta(days=30), 30.00)
        self.assertEqual(future_membership.remaining_days(self.today), 0)

    @patch('datetime.date')
    def test_membership_to_dict(self, mock_date):
        mock_date.today.return_value = self.today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
        membership = Membership("Monthly", self.today, self.future_date, 30.00)
        expected_dict = {
            "plan_name": "Monthly",
            "start_date": self.today.isoformat(),
            "end_date": self.future_date.isoformat(),
            "fee": 30.00,
            "is_active": True
        }
        self.assertDictEqual(membership.to_dict(), expected_dict)

        # Test inactive membership to_dict
        inactive_membership = Membership("Annual", datetime.date(2022, 1, 1), datetime.date(2022, 12, 31), 300.00)
        expected_inactive_dict = {
            "plan_name": "Annual",
            "start_date": datetime.date(2022, 1, 1).isoformat(),
            "end_date": datetime.date(2022, 12, 31).isoformat(),
            "fee": 300.00,
            "is_active": False
        }
        self.assertDictEqual(inactive_membership.to_dict(), expected_inactive_dict)

class TestFitnessClass(unittest.TestCase):
    def setUp(self):
        self.now = datetime.datetime(2023, 1, 15, 10, 0, 0)
        self.class_start = self.now + datetime.timedelta(hours=1)
        self.class_end = self.class_start + datetime.timedelta(hours=1)
        self.past_class_start = self.now - datetime.timedelta(hours=2)
        self.past_class_end = self.now - datetime.timedelta(hours=1)

    def test_fitness_class_initialization(self):
        f_class = FitnessClass("c1", "Yoga", self.class_start, self.class_end, 10)
        self.assertEqual(f_class.class_id, "c1")
        self.assertEqual(f_class.name, "Yoga")
        self.assertEqual(f_class.start_datetime, self.class_start)
        self.assertEqual(f_class.end_datetime, self.class_end)
        self.assertEqual(f_class.capacity, 10)
        self.assertEqual(f_class.enrolled_members, [])
        self.assertEqual(f_class.attended_members, [])

    def test_is_full(self):
        f_class = FitnessClass("c1", "Yoga", self.class_start, self.class_end, 2)
        self.assertFalse(f_class.is_full())
        f_class.enrolled_members.append("m1")
        self.assertFalse(f_class.is_full())
        f_class.enrolled_members.append("m2")
        self.assertTrue(f_class.is_full())
        f_class.enrolled_members.append("m3") # Over capacity
        self.assertTrue(f_class.is_full())

    @patch('datetime.datetime')
    def test_is_ongoing_or_past(self, mock_datetime):
        mock_datetime.now.return_value = self.now
        mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw) # Allow normal datetime object creation

        # Future class
        future_class = FitnessClass("c1", "Yoga", self.class_start, self.class_end, 10)
        self.assertFalse(future_class.is_ongoing_or_past(self.now))
        self.assertFalse(future_class.is_ongoing_or_past()) # Test with default now

        # Past class
        past_class = FitnessClass("c2", "Zumba", self.past_class_start, self.past_class_end, 10)
        self.assertTrue(past_class.is_ongoing_or_past(self.now))
        self.assertTrue(past_class.is_ongoing_or_past()) # Test with default now

        # Currently ongoing class
        ongoing_class = FitnessClass("c3", "Spin", self.now - datetime.timedelta(minutes=10), self.now + datetime.timedelta(minutes=10), 10)
        self.assertTrue(ongoing_class.is_ongoing_or_past(self.now))

        # Class starts exactly now
        starts_now_class = FitnessClass("c4", "Pilates", self.now, self.now + datetime.timedelta(minutes=60), 10)
        self.assertTrue(starts_now_class.is_ongoing_or_past(self.now))

    def test_overlaps_with(self):
        # Class 1: 10:00 - 11:00
        class1 = FitnessClass("c1", "Yoga", datetime.datetime(2023, 1, 15, 10, 0), datetime.datetime(2023, 1, 15, 11, 0), 10)

        # Class 2: 10:30 - 11:30 (Overlap)
        class2 = FitnessClass("c2", "Zumba", datetime.datetime(2023, 1, 15, 10, 30), datetime.datetime(2023, 1, 15, 11, 30), 10)
        self.assertTrue(class1.overlaps_with(class2))
        self.assertTrue(class2.overlaps_with(class1))

        # Class 3: 09:00 - 10:30 (Overlap)
        class3 = FitnessClass("c3", "Pilates", datetime.datetime(2023, 1, 15, 9, 0), datetime.datetime(2023, 1, 15, 10, 30), 10)
        self.assertTrue(class1.overlaps_with(class3))
        self.assertTrue(class3.overlaps_with(class1))

        # Class 4: 11:00 - 12:00 (No overlap - exact end/start)
        class4 = FitnessClass("c4", "Spin", datetime.datetime(2023, 1, 15, 11, 0), datetime.datetime(2023, 1, 15, 12, 0), 10)
        self.assertFalse(class1.overlaps_with(class4))
        self.assertFalse(class4.overlaps_with(class1))

        # Class 5: 09:00 - 09:30 (No overlap)
        class5 = FitnessClass("c5", "Aqua", datetime.datetime(2023, 1, 15, 9, 0), datetime.datetime(2023, 1, 15, 9, 30), 10)
        self.assertFalse(class1.overlaps_with(class5))
        self.assertFalse(class5.overlaps_with(class1))

        # Class 6: 10:15 - 10:45 (Class 6 fully within Class 1)
        class6 = FitnessClass("c6", "Boxing", datetime.datetime(2023, 1, 15, 10, 15), datetime.datetime(2023, 1, 15, 10, 45), 10)
        self.assertTrue(class1.overlaps_with(class6))
        self.assertTrue(class6.overlaps_with(class1))

    @patch('datetime.datetime')
    def test_fitness_class_to_dict(self, mock_datetime):
        mock_datetime.now.return_value = self.now
        mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw) # Allow normal datetime object creation

        f_class = FitnessClass("c1", "Yoga", self.class_start, self.class_end, 5)
        f_class.enrolled_members.extend(["m1", "m2"])
        f_class.attended_members.append("m1")

        expected_dict_no_members = {
            "class_id": "c1",
            "name": "Yoga",
            "start_datetime": self.class_start.isoformat(),
            "end_datetime": self.class_end.isoformat(),
            "capacity": 5,
            "enrolled_count": len(f_class.enrolled_members), # Use len(f_class.enrolled_members) for accuracy
            "is_full": False
        }
        self.assertDictEqual(f_class.to_dict(), expected_dict_no_members)

        expected_dict_with_members = {
            "class_id": "c1",
            "name": "Yoga",
            "start_datetime": self.class_start.isoformat(),
            "end_datetime": self.class_end.isoformat(),
            "capacity": 5,
            "enrolled_count": len(f_class.enrolled_members), # Use len(f_class.enrolled_members) for accuracy
            "is_full": False,
            "enrolled_members": ["m1", "m2"],
            "attended_members": ["m1"]
        }
        self.assertDictEqual(f_class.to_dict(include_members=True), expected_dict_with_members)

        # Test with full class
        full_class = FitnessClass("c2", "Spin", self.class_start, self.class_end, 1)
        full_class.enrolled_members.append("m10")
        self.assertTrue(full_class.to_dict()["is_full"])

class TestPayment(unittest.TestCase):
    def setUp(self):
        self.payment_date = datetime.datetime(2023, 1, 15, 10, 30, 0)

    def test_payment_initialization(self):
        payment = Payment("p1", "m1", 50.0, self.payment_date, "Cash", "Training Session")
        self.assertEqual(payment.payment_id, "p1")
        self.assertEqual(payment.member_id, "m1")
        self.assertEqual(payment.amount, 50.0)
        self.assertEqual(payment.date, self.payment_date)
        self.assertEqual(payment.method, "Cash")
        self.assertEqual(payment.description, "Training Session")

    def test_to_dict(self):
        payment = Payment("p2", "m2", 100.0, self.payment_date, "Credit Card", "Annual Fee")
        expected_dict = {
            "payment_id": "p2",
            "member_id": "m2",
            "amount": 100.0,
            "date": self.payment_date.isoformat(),
            "method": "Credit Card",
            "description": "Annual Fee"
        }
        self.assertDictEqual(payment.to_dict(), expected_dict)

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account()
        self.today = datetime.date(2023, 1, 15)
        self.now = datetime.datetime(2023, 1, 15, 12, 0, 0)

        # Mock datetime.date.today and datetime.datetime.now globally for Account tests
        self.patcher_date = patch('datetime.date')
        self.mock_date = self.patcher_date.start()
        self.mock_date.today.return_value = self.today
        self.mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

        self.patcher_datetime = patch('datetime.datetime')
        self.mock_datetime = self.patcher_datetime.start()
        self.mock_datetime.now.return_value = self.now
        self.mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)

        # Mock uuid.uuid4 to return predictable UUIDs
        self.patcher_uuid = patch('uuid.uuid4')
        self.mock_uuid_instance = self.patcher_uuid.start()
        
        # Create a generator for mock UUID objects
        self._uuid_counter = 0
        def uuid_hex_generator():
            while True:
                self._uuid_counter += 1
                mock_obj = MagicMock()
                mock_obj.hex = f'mock_uuid_{self._uuid_counter:03d}' 
                yield mock_obj

        self.mock_uuid_instance.side_effect = uuid_hex_generator()
        
        # Capture print output
        self.patcher_print = patch('builtins.print')
        self.mock_print = self.patcher_print.start()

    def tearDown(self):
        self.patcher_date.stop()
        self.patcher_datetime.stop()
        self.patcher_uuid.stop()
        self.patcher_print.stop()

    # --- Member Management Tests ---
    def test_create_member(self):
        member_id = self.account.create_member("Alice", "alice@example.com")
        self.assertIsNotNone(member_id) 
        self.assertIn(member_id, self.account._members)
        self.assertEqual(self.account._members[member_id].name, "Alice")
        self.assertEqual(self.account._memberships[member_id], [])
        self.assertEqual(member_id, 'mock_uuid_001') # Ensure first UUID is as expected

        member_id_2 = self.account.create_member("Bob", "bob@example.com")
        self.assertIsNotNone(member_id_2)
        self.assertNotEqual(member_id, member_id_2)
        self.assertEqual(member_id_2, 'mock_uuid_002') # Ensure second UUID is as expected


    def test_get_member_details(self):
        member_id = self.account.create_member("Charlie", "charlie@example.com")
        details = self.account.get_member_details(member_id)
        self.assertIsNotNone(details)
        self.assertEqual(details["name"], "Charlie")
        self.assertEqual(details["member_id"], member_id)

        self.assertIsNone(self.account.get_member_details("non_existent_id"))

    def test_get_all_members_details(self):
        self.assertEqual(self.account.get_all_members_details(), [])

        self.account.create_member("Alice", "a@example.com")
        self.account.create_member("Bob", "b@example.com")
        all_members = self.account.get_all_members_details()
        self.assertEqual(len(all_members), 2)
        self.assertTrue(any(m['name'] == 'Alice' for m in all_members))
        self.assertTrue(any(m['name'] == 'Bob' for m in all_members))
        self.assertIsInstance(all_members[0]['member_id'], str) 

    # --- Membership Management Tests ---
    def test_purchase_membership_success(self):
        member_id = self.account.create_member("Dave", "dave@example.com")
        self.mock_print.reset_mock() # Reset after create_member print if any

        # Test Monthly
        success = self.account.purchase_membership(member_id, "Monthly", "Credit Card")
        self.assertTrue(success)
        self.assertEqual(len(self.account._memberships[member_id]), 1)
        membership = self.account._memberships[member_id][0]
        self.assertEqual(membership.plan_name, "Monthly")
        self.assertEqual(membership.fee, 30.00)
        self.assertEqual(membership.start_date, self.today)
        self.assertEqual(membership.end_date, self.today + datetime.timedelta(days=30))
        self.assertEqual(len(self.account._payments), 1)
        self.assertEqual(self.account._payments[0].description, "Monthly Membership Purchase")
        self.mock_print.assert_not_called() # No errors printed

        # Test Annual for another member
        member_id_2 = self.account.create_member("Eve", "eve@example.com")
        success_annual = self.account.purchase_membership(member_id_2, "Annual", "Cash")
        self.assertTrue(success_annual)
        self.assertEqual(len(self.account._memberships[member_id_2]), 1)
        membership_annual = self.account._memberships[member_id_2][0]
        self.assertEqual(membership_annual.plan_name, "Annual")
        self.assertEqual(membership_annual.fee, 300.00)
        self.assertEqual(membership_annual.start_date, self.today)
        self.assertEqual(membership_annual.end_date, self.today + datetime.timedelta(days=365))
        self.assertEqual(len(self.account._payments), 2)


    def test_purchase_membership_failure_member_not_found(self):
        success = self.account.purchase_membership("non_existent", "Monthly", "Credit Card")
        self.assertFalse(success)
        self.mock_print.assert_called_with("Error: Member with ID non_existent not found.")

    def test_purchase_membership_failure_invalid_plan(self):
        member_id = self.account.create_member("Frank", "frank@example.com")
        self.mock_print.reset_mock() # Reset after create_member's print if any
        success = self.account.purchase_membership(member_id, "InvalidPlan", "Cash")
        self.assertFalse(success)
        self.mock_print.assert_called_with("Error: Invalid or unknown membership plan 'InvalidPlan'.")

    @patch('datetime.date')
    def test_is_membership_active(self, mock_date):
        mock_date.today.return_value = self.today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

        member_id_active = self.account.create_member("Grace", "grace@example.com")
        self.mock_print.reset_mock()
        self.account.purchase_membership(member_id_active, "Monthly", "Credit Card") 
        self.mock_print.reset_mock() # Reset after successful purchase print

        member_id_inactive_future = self.account.create_member("Heidi", "heidi@example.com")
        # Manually add a future membership (no payment recorded for this test setup)
        future_start = self.today + datetime.timedelta(days=10)
        future_end = future_start + datetime.timedelta(days=30)
        self.account._memberships[member_id_inactive_future].append(Membership("Monthly", future_start, future_end, 30.0))

        member_id_inactive_past = self.account.create_member("Ivan", "ivan@example.com")
        # Manually add a past membership (no payment recorded for this test setup)
        past_start = self.today - datetime.timedelta(days=60)
        past_end = self.today - datetime.timedelta(days=30)
        self.account._memberships[member_id_inactive_past].append(Membership("Monthly", past_start, past_end, 30.0))

        # Test active
        self.assertTrue(self.account.is_membership_active(member_id_active))

        # Test inactive (future)
        self.assertFalse(self.account.is_membership_active(member_id_inactive_future))

        # Test inactive (past)
        self.assertFalse(self.account.is_membership_active(member_id_inactive_past))

        # Test non-existent member
        self.assertFalse(self.account.is_membership_active("non_existent"))

        # Test member with no memberships
        member_id_no_membership = self.account.create_member("Jane", "jane@example.com")
        self.assertFalse(self.account.is_membership_active(member_id_no_membership))

    @patch('datetime.date')
    def test_get_membership_remaining_days(self, mock_date):
        mock_date.today.return_value = self.today
        mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)

        member_id = self.account.create_member("Kyle", "kyle@example.com")
        self.mock_print.reset_mock()
        self.account.purchase_membership(member_id, "Monthly", "Credit Card")
        self.mock_print.reset_mock()
        # Membership ends self.today + 30 days = 30 days remaining
        self.assertEqual(self.account.get_membership_remaining_days(member_id), 30)

        # Advance time by 10 days
        mock_date.today.return_value = self.today + datetime.timedelta(days=10)
        self.assertEqual(self.account.get_membership_remaining_days(member_id), 20)

        # Membership expired
        mock_date.today.return_value = self.today + datetime.timedelta(days=31)
        self.assertEqual(self.account.get_membership_remaining_days(member_id), 0)

        # Non-existent member
        self.assertEqual(self.account.get_membership_remaining_days("non_existent"), 0)

        # Member with no membership
        member_id_no_membership = self.account.create_member("Liam", "liam@example.com")
        self.assertEqual(self.account.get_membership_remaining_days(member_id_no_membership), 0)

    # --- Fitness Class Management Tests ---
    def test_add_class(self):
        class_id = self.account.add_class("Spin", self.now, 60, 15)
        self.assertIsNotNone(class_id)
        self.assertIn(class_id, self.account._classes)
        f_class = self.account._classes[class_id]
        self.assertEqual(f_class.name, "Spin")
        self.assertEqual(f_class.start_datetime, self.now)
        self.assertEqual(f_class.end_datetime, self.now + datetime.timedelta(minutes=60))
        self.assertEqual(f_class.capacity, 15)

    def test_enroll_in_class_success(self):
        member_id = self.account.create_member("Mia", "mia@example.com")
        self.account.purchase_membership(member_id, "Monthly", "Card")
        class_id = self.account.add_class("Yoga", self.now + datetime.timedelta(hours=1), 60, 5)
        self.mock_print.reset_mock()
        
        success = self.account.enroll_in_class(member_id, class_id)
        self.assertTrue(success)
        self.assertIn(member_id, self.account._classes[class_id].enrolled_members)
        self.mock_print.assert_called_with(f"Member {member_id} successfully enrolled in 'Yoga'.")

    def test_enroll_in_class_failure_member_not_found(self):
        class_id = self.account.add_class("Yoga", self.now + datetime.timedelta(hours=1), 60, 5)
        self.mock_print.reset_mock()
        success = self.account.enroll_in_class("non_existent_member", class_id)
        self.assertFalse(success)
        self.mock_print.assert_called_with("Enrollment Error: Member non_existent_member not found.")

    def test_enroll_in_class_failure_class_not_found(self):
        member_id = self.account.create_member("Nora", "nora@example.com")
        self.account.purchase_membership(member_id, "Monthly", "Card")
        self.mock_print.reset_mock()
        success = self.account.enroll_in_class(member_id, "non_existent_class")
        self.assertFalse(success)
        self.mock_print.assert_called_with("Enrollment Error: Class non_existent_class not found.")

    def test_enroll_in_class_failure_no_active_membership(self):
        member_id = self.account.create_member("Oscar", "oscar@example.com")
        # Do not purchase membership
        class_id = self.account.add_class("Pilates", self.now + datetime.timedelta(hours=1), 60, 5)
        self.mock_print.reset_mock()
        success = self.account.enroll_in_class(member_id, class_id)
        self.assertFalse(success)
        self.mock_print.assert_called_with(f"Enrollment Error: Member {member_id} does not have an active membership.")

    def test_enroll_in_class_failure_class_full(self):
        member_id_1 = self.account.create_member("Paul", "paul@example.com")
        self.account.purchase_membership(member_id_1, "Monthly", "Card")
        member_id_2 = self.account.create_member("Quinn", "quinn@example.com")
        self.account.purchase_membership(member_id_2, "Monthly", "Card")

        class_id = self.account.add_class("Zumba", self.now + datetime.timedelta(hours=1), 60, 1) # Capacity 1
        
        # First enrollment succeeds
        self.account.enroll_in_class(member_id_1, class_id)
        self.mock_print.reset_mock()
        
        success = self.account.enroll_in_class(member_id_2, class_id) # Try to enroll second
        self.assertFalse(success)
        self.mock_print.assert_called_with("Enrollment Error: Class 'Zumba' is full.")

    def test_enroll_in_class_failure_already_enrolled(self):
        member_id = self.account.create_member("Rachel", "rachel@example.com")
        self.account.purchase_membership(member_id, "Monthly", "Card")
        class_id = self.account.add_class("Boxing", self.now + datetime.timedelta(hours=1), 60, 5)
        
        # First enrollment succeeds
        self.account.enroll_in_class(member_id, class_id)
        self.mock_print.reset_mock()
        success = self.account.enroll_in_class(member_id, class_id) # Enroll again
        self.assertFalse(success)
        self.mock_print.assert_called_with(f"Enrollment Error: Member {member_id} already enrolled in 'Boxing'.")

    def test_enroll_in_class_failure_overlapping_class(self):
        member_id = self.account.create_member("Sam", "sam@example.com")
        self.account.purchase_membership(member_id, "Monthly", "Card")

        # Class 1: 10:00 - 11:00 (next day, relative to mock_now = 2023-01-15 12:00:00)
        class1_start = self.now + datetime.timedelta(days=1, hours=-2, minutes=0) # E.g., 2023-01-16 10:00:00
        class1_end = class1_start + datetime.timedelta(hours=1)
        class_id_1 = self.account.add_class("Morning Yoga", class1_start, 60, 5)
        self.account.enroll_in_class(member_id, class_id_1)
        self.mock_print.reset_mock()

        # Class 2: 10:30 - 11:30 (overlaps with Class 1)
        class2_start = self.now + datetime.timedelta(days=1, hours=-1, minutes=30) # E.g., 2023-01-16 10:30:00
        class2_end = class2_start + datetime.timedelta(hours=1)
        class_id_2 = self.account.add_class("Midday Spin", class2_start, 60, 5)
        
        success = self.account.enroll_in_class(member_id, class_id_2)
        self.assertFalse(success)
        expected_message = f"Enrollment Error: Member {member_id} has an overlapping class 'Morning Yoga' ({class1_start.strftime('%Y-%m-%d %H:%M')})."
        self.mock_print.assert_called_with(expected_message)

    def test_cancel_class_enrollment_success(self):
        member_id = self.account.create_member("Tina", "tina@example.com")
        self.account.purchase_membership(member_id, "Monthly", "Card")
        class_id = self.account.add_class("Dance", self.now + datetime.timedelta(hours=1), 60, 5)
        self.account.enroll_in_class(member_id, class_id)
        self.mock_print.reset_mock()

        success = self.account.cancel_class_enrollment(member_id, class_id)
        self.assertTrue(success)
        self.assertNotIn(member_id, self.account._classes[class_id].enrolled_members)
        self.mock_print.assert_called_with(f"Member {member_id} successfully cancelled enrollment from 'Dance'.")

    def test_cancel_class_enrollment_failure_class_not_found(self):
        member_id = self.account.create_member("Ulysses", "ulysses@example.com")
        self.mock_print.reset_mock()
        success = self.account.cancel_class_enrollment(member_id, "non_existent_class")
        self.assertFalse(success)
        self.mock_print.assert_called_with("Cancellation Error: Class non_existent_class not found.")

    def test_cancel_class_enrollment_failure_not_enrolled(self):\n        member_id = self.account.create_member(\"Vera\", \"vera@example.com\")\n        self.account.purchase_membership(member_id, \"Monthly\", \"Card\")\n        class_id = self.account.add_class(\"Spin\", self.now + datetime.timedelta(hours=1), 60, 5)\n        self.mock_print.reset_mock()\n        \n        success = self.account.cancel_class_enrollment(member_id, class_id)\n        self.assertFalse(success)\n        self.mock_print.assert_called_with(f\"Cancellation Error: Member {member_id} not enrolled in class 'Spin'.\")\n\n    def test_cancel_class_enrollment_failure_class_started(self):\n        member_id = self.account.create_member(\"Walter\", \"walter@example.com\")\n        self.account.purchase_membership(member_id, \"Monthly\", \"Card\")\n        # Class started in the past relative to mock_now\n        class_id = self.account.add_class(\"Kickboxing\", self.now - datetime.timedelta(minutes=30), 60, 5)\n        self.account.enroll_in_class(member_id, class_id)\n        self.mock_print.reset_mock()\n\n        success = self.account.cancel_class_enrollment(member_id, class_id)\n        self.assertFalse(success)\n        self.mock_print.assert_called_with(\"Cancellation Error: Cannot cancel attendance, class 'Kickboxing' has already started or passed.\")\n\n    def test_record_class_attendance(self):\n        member_id_1 = self.account.create_member(\"Xavier\", \"xavier@example.com\")\n        member_id_2 = self.account.create_member(\"Yvonne\", \"yvonne@example.com\")\n        member_id_3 = self.account.create_member(\"Zoe\", \"zoe@example.com\")\n        self.account.purchase_membership(member_id_1, \"Monthly\", \"Card\")\n        self.account.purchase_membership(member_id_2, \"Monthly\", \"Card\")\n        self.account.purchase_membership(member_id_3, \"Monthly\", \"Card\")\n\n        class_id = self.account.add_class(\"HIIT\", self.now + datetime.timedelta(hours=1), 45, 5)\n        self.account.enroll_in_class(member_id_1, class_id)\n        self.account.enroll_in_class(member_id_2, class_id)\n\n        # Record attendance for enrolled members\n        self.mock_print.reset_mock()\n        results = self.account.record_class_attendance(class_id, [member_id_1, member_id_2])\n        self.assertTrue(results[member_id_1])\n        self.assertTrue(results[member_id_2])\n        self.assertIn(member_id_1, self.account._classes[class_id].attended_members)\n        self.assertIn(member_id_2, self.account._classes[class_id].attended_members)\n        self.assertFalse(self.mock_print.called) # No warnings if all are enrolled\n\n        # Try to record attendance for a non-enrolled member\n        self.mock_print.reset_mock()\n        results_non_enrolled = self.account.record_class_attendance(class_id, [member_id_3])\n        self.assertFalse(results_non_enrolled[member_id_3])\n        self.assertNotIn(member_id_3, self.account._classes[class_id].attended_members)\n        self.mock_print.assert_called_with(f\"Attendance Warning: Member {member_id_3} not enrolled or already marked present for class 'HIIT'.\")\n\n        # Try to record attendance for an already attended member\n        self.mock_print.reset_mock()\n        results_already_attended = self.account.record_class_attendance(class_id, [member_id_1])\n        self.assertFalse(results_already_attended[member_id_1])\n        # Check that member_id_1 is still only in attended_members once\n        self.assertEqual(self.account._classes[class_id].attended_members.count(member_id_1), 1)\n        self.mock_print.assert_called_with(f\"Attendance Warning: Member {member_id_1} not enrolled or already marked present for class 'HIIT'.\")\n\n        # Non-existent class\n        self.mock_print.reset_mock()\n        results_no_class = self.account.record_class_attendance(\"non_existent_class\", [member_id_1])\n        self.assertFalse(results_no_class[member_id_1])\n        self.mock_print.assert_called_with(\"Attendance Error: Class non_existent_class not found.\")\n\n    # --- Payment & Revenue Management Tests ---\n    def test_record_payment_success(self):\n        member_id = self.account.create_member(\"Adam\", \"adam@example.com\")\n        self.mock_print.reset_mock() # Reset after create_member\n        payment_id = self.account.record_payment(member_id, 150.0, self.now, \"Bank Transfer\", \"Personal Training\")\n        self.assertIsNotNone(payment_id) \n        self.assertEqual(len(self.account._payments), 1)\n        payment = self.account._payments[0]\n        self.assertEqual(payment.member_id, member_id)\n        self.assertEqual(payment.amount, 150.0)\n        self.assertEqual(payment.description, \"Personal Training\")\n        self.mock_print.assert_not_called() # No errors printed\n\n    def test_record_payment_failure_member_not_found(self):\n        self.mock_print.reset_mock()\n        payment_id = self.account.record_payment(\"unknown_member\", 25.0, self.now, \"Cash\", \"Towel Rental\")\n        self.assertEqual(payment_id, \"\")\n        self.assertEqual(len(self.account._payments), 0)\n        self.mock_print.assert_called_with(\"Payment Error: Member unknown_member not found.\")\n\n    def test_get_total_revenue(self):\n        member_id_1 = self.account.create_member(\"Ben\", \"ben@example.com\")\n        member_id_2 = self.account.create_member(\"Cathy\", \"cathy@example.com\")\n        self.mock_print.reset_mock()\n\n        self.account.record_payment(member_id_1, 50.0, self.now, \"Cash\", \"Item 1\")\n        self.account.record_payment(member_id_2, 75.50, self.now, \"Card\", \"Item 2\")\n        self.account.record_payment(member_id_1, 20.0, self.now, \"Cash\", \"Item 3\")\n        \n        self.assertEqual(self.account.get_total_revenue(), 50.0 + 75.50 + 20.0)\n\n        # Test with no payments\n        new_account = Account()\n        self.assertEqual(new_account.get_total_revenue(), 0.0)\n\n    # --- Reporting Methods ---\n    def test_get_member_class_schedule(self):\n        member_id = self.account.create_member(\"Diana\", \"diana@example.com\")\n        self.account.purchase_membership(member_id, \"Monthly\", \"Card\")\n\n        class_id_1 = self.account.add_class(\"Morning Yoga\", self.now + datetime.timedelta(hours=1), 60, 5)\n        class_id_2 = self.account.add_class(\"Evening Spin\", self.now + datetime.timedelta(hours=5), 45, 10)\n        class_id_3 = self.account.add_class(\"Past Class\", self.now - datetime.timedelta(hours=2), 60, 5)\n\n        self.account.enroll_in_class(member_id, class_id_1)\n        self.account.enroll_in_class(member_id, class_id_2)\n        # Do not enroll in class_id_3 to test only enrolled classes\n\n        schedule = self.account.get_member_class_schedule(member_id)\n        self.assertEqual(len(schedule), 2)\n        self.assertTrue(any(c['name'] == \"Morning Yoga\" for c in schedule))\n        self.assertTrue(any(c['name'] == \"Evening Spin\" for c in schedule))\n        self.assertFalse(any(c['name'] == \"Past Class\" for c in schedule))\n\n        schedule_ids = self.account.get_member_class_schedule(member_id, return_ids_only=True)\n        self.assertEqual(len(schedule_ids), 2)\n        self.assertIn(class_id_1, schedule_ids)\n        self.assertIn(class_id_2, schedule_ids)\n\n        self.assertEqual(self.account.get_member_class_schedule(\"non_existent_member\"), [])\n        member_no_classes = self.account.create_member(\"Emma\", \"emma@example.com\")\n        self.assertEqual(self.account.get_member_class_schedule(member_no_classes), [])\n\n    def test_get_member_attendance_history(self):\n        member_id = self.account.create_member(\"Fred\", \"fred@example.com\")\n        self.account.purchase_membership(member_id, \"Monthly\", \"Card\")\n\n        # Class in the past, attended\n        past_attended_class_id = self.account.add_class(\"Morning Run\", self.now - datetime.timedelta(hours=2), 60, 5)\n        self.account.enroll_in_class(member_id, past_attended_class_id)\n        self.account.record_class_attendance(past_attended_class_id, [member_id])\n\n        # Class in the past, enrolled but not attended\n        past_missed_class_id = self.account.add_class(\"Evening Stretch\", self.now - datetime.timedelta(hours=3), 45, 5)\n        self.account.enroll_in_class(member_id, past_missed_class_id)\n\n        # Class in the future, enrolled\n        future_class_id = self.account.add_class(\"Future HIIT\", self.now + datetime.timedelta(hours=1), 60, 5)\n        self.account.enroll_in_class(member_id, future_class_id)\n\n        history = self.account.get_member_attendance_history(member_id)\n        self.assertEqual(len(history), 2) # Should only include past/ongoing classes\n        \n        # Check attended class\n        attended_entry = next(c for c in history if c['class_id'] == past_attended_class_id)\n        self.assertIsNotNone(attended_entry)\n        self.assertTrue(attended_entry['attended'])\n\n        # Check missed class\n        missed_entry = next(c for c in history if c['class_id'] == past_missed_class_id)\n        self.assertIsNotNone(missed_entry)\n        self.assertFalse(missed_entry['attended'])\n\n        # Ensure future class is not in history\n        self.assertFalse(any(c['class_id'] == future_class_id for c in history))\n\n        self.assertEqual(self.account.get_member_attendance_history(\"non_existent\"), [])\n        member_no_history = self.account.create_member(\"Gary\", \"gary@example.com\")\n        self.assertEqual(self.account.get_member_attendance_history(member_no_history), [])\n\n    def test_get_member_transactions(self):\n        member_id_1 = self.account.create_member(\"Hannah\", \"hannah@example.com\")\n        member_id_2 = self.account.create_member(\"Ian\", \"ian@example.com\")\n\n        # Add payments\n        self.account.record_payment(member_id_1, 50.0, self.now - datetime.timedelta(days=10), \"Cash\", \"PT Session\")\n        self.account.record_payment(member_id_1, 30.0, self.now - datetime.timedelta(days=5), \"Card\", \"T-shirt\")\n        self.account.record_payment(member_id_2, 80.0, self.now - datetime.timedelta(days=7), \"Bank\", \"Locker Rental\")\n\n        transactions_hannah = self.account.get_member_transactions(member_id_1)\n        self.assertEqual(len(transactions_hannah), 2)\n        self.assertTrue(any(t['amount'] == 50.0 for t in transactions_hannah))\n        self.assertTrue(any(t['amount'] == 30.0 for t in transactions_hannah))\n\n        transactions_ian = self.account.get_member_transactions(member_id_2)\n        self.assertEqual(len(transactions_ian), 1)\n        self.assertTrue(any(t['amount'] == 80.0 for t in transactions_ian))\n\n        self.assertEqual(self.account.get_member_transactions(\"non_existent\"), [])\n        member_no_transactions = self.account.create_member(\"Jake\", \"jake@example.com\")\n        self.assertEqual(self.account.get_member_transactions(member_no_transactions), [])\n\n    def test_list_available_classes(self):\n        class_id_1 = self.account.add_class(\"Morning Yoga\", self.now + datetime.timedelta(hours=1), 60, 5)\n        class_id_2 = self.account.add_class(\"Evening Spin\", self.now + datetime.timedelta(hours=5), 45, 10)\n        class_id_3 = self.account.add_class(\"Empty Class\", self.now + datetime.timedelta(hours=2), 30, 2)\n\n        member_id_1 = self.account.create_member(\"Leo\", \"leo@example.com\")\n        self.account.purchase_membership(member_id_1, \"Monthly\", \"Card\")\n        self.account.enroll_in_class(member_id_1, class_id_1)\n        self.account.enroll_in_class(member_id_1, class_id_3)\n\n        available_classes = self.account.list_available_classes()\n        self.assertEqual(len(available_classes), 3)\n\n        yoga_class = next(c for c in available_classes if c['class_id'] == class_id_1)\n        self.assertEqual(yoga_class[\"enrolled_count\"], 1)\n        self.assertEqual(yoga_class[\"remaining_capacity\"], 4)\n        self.assertFalse(yoga_class[\"is_full\"])\n\n        spin_class = next(c for c in available_classes if c['class_id'] == class_id_2)\n        self.assertEqual(spin_class[\"enrolled_count\"], 0)\n        self.assertEqual(spin_class[\"remaining_capacity\"], 10)\n        self.assertFalse(spin_class[\"is_full\"])\n\n        empty_class = next(c for c in available_classes if c['class_id'] == class_id_3)\n        self.assertEqual(empty_class[\"enrolled_count\"], 1)\n        self.assertEqual(empty_class[\"remaining_capacity\"], 1)\n        self.assertFalse(empty_class[\"is_full\"])\n\n\nif __name__ == '__main__':
    unittest.main()
```