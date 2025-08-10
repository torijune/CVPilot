from backend.app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")

def handler_func(request):
    return handler(request, {}) 