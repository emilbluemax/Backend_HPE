import structlog

class StructLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            structlog.get_logger().bind(user_id=request.user.id)
        else:
            structlog.get_logger().bind(user_id=None)
        response = self.get_response(request)
        return response