#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from full_stack.crew import FullStack

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")




def run():
    """
    Run the research crew.
    """
    requirements = """
    A simple gym management system for a fitness club.

The system should allow members to create an account, storing name, contact information, and a unique member ID.

The system should allow members to purchase a membership plan (e.g., Monthly, Quarterly, Annual) by paying the associated fee.

The system should track membership start and end dates and mark a membership as active or expired.

The system should allow members to enroll in or cancel fitness classes, providing the class name and date/time.

The system should track class capacity and prevent enrollment if the class is full.

The system should allow trainers to record attendance for each class, marking which members were present.

The system should record payments made by members (amount, date, method).

The system should calculate the remaining days on a member’s active plan and the total revenue collected from all members.

The system should be able to report a member’s class schedule and attendance history at any point in time.

The system should be able to list all transactions (membership purchases and class fees) made by a member over time.

The system should prevent actions that violate business rules, such as:

Enrolling in a class without an active membership.

Enrolling in two classes that overlap in time.

Canceling attendance after the class has started.

The system has access to a helper function get_membership_fee(plan_name) that returns the current price for a membership plan and includes a test implementation that returns fixed fees for "Monthly", "Quarterly", and "Annual".
    """
    module_name = "accounts"
    class_name = "Account"
    
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Create and run the crew
    result = FullStack().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()
