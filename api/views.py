from django.http import JsonResponse


def api_root(request):
    return JsonResponse({"status": "ok", "message": "API module placeholder"})
