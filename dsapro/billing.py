# billing.py
def calculate_bill(base_fee: float, tests_cost: float = 0.0, medicine_cost: float = 0.0, other: float = 0.0) -> float:
    """
    Simple billing calculation. Return total amount.
    """
    total = float(base_fee) + float(tests_cost) + float(medicine_cost) + float(other)
    return round(total, 2)