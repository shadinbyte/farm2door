"""
Main project views - Health check and utilities
"""

import sys

from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers
    Returns system status and database connectivity
    """
    try:
        # Check database connection
        connection.ensure_connection()
        db_status = "connected"
        db_error = None
    except Exception as e:
        db_status = "disconnected"
        db_error = str(e)

    # Overall health status
    is_healthy = db_status == "connected"
    status_code = 200 if is_healthy else 503

    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "version": "1.0.0",
        "database": {"status": db_status, "error": db_error},
        "python_version": sys.version,
        "debug_mode": settings.DEBUG,
    }

    return JsonResponse(response_data, status=status_code)
