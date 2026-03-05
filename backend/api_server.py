"""CareerLens API server bootstrap."""

from app.app_factory import create_app
from core.config import HOST, PORT

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host=HOST, port=PORT, reload=True)
