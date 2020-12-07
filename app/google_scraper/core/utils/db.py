from django.db.models import Func


class Round(Func):
    """
    Round to one decimal place Django model aggregates.
    """
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 1)'
