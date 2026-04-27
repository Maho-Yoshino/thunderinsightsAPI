from fastapi import FastAPI
from app.routers import users_routers_v1

description = """
Thunderinsights API used internally to refresh player data
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations correlating to getting information about the users/players of the game War Thunder.",
    }
]

def create_app():
    app = FastAPI(
        title="Thunderinsights API",
        description=description,
        summary="API to retrieve War Thunder player data.",
        version="0.0.1",
        openapi_tags=tags_metadata,
        root_path="/api",
    )

    app.include_router(users_routers_v1.router, prefix="/v1")
    #app.include_router(users_routers_v1.router, prefix="/latest")

    return app


app = create_app()