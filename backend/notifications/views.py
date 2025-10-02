from django.http import JsonResponse


def index(request):
    return JsonResponse({"message": "Notifications app is working"})
