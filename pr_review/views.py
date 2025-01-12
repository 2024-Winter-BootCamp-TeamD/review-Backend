from django.http import JsonResponse


def hello_view(request):
    return JsonResponse({"message": "hello"})