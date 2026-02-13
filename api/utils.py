import json

from django.http import JsonResponse


def json_ok(data, status=200):
    return JsonResponse({"ok": True, "data": data}, status=status)


def json_error(code, message, status=400, details=None):
    return JsonResponse(
        {
            "ok": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
        status=status,
    )


def parse_json_body(request):
    try:
        raw = request.body.decode("utf-8")
    except UnicodeDecodeError:
        return None, json_error(
            code="invalid_json",
            message="Тело запроса должно быть в UTF-8.",
            status=400,
        )

    if not raw.strip():
        return {}, None

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, json_error(
            code="invalid_json",
            message="Некорректный JSON.",
            status=400,
            details={"position": exc.pos},
        )

    if not isinstance(payload, dict):
        return None, json_error(
            code="invalid_json",
            message="JSON должен быть объектом.",
            status=400,
        )

    return payload, None
