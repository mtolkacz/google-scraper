from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class ResultsNotFound(APIException):
    """
    Raised when no results found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Raised when no results found.')
