from fastapi import APIRouter
from app.routes import auth_route, user_route, gig_routes, chat_route, buddy_routes

api_router = APIRouter()

api_router.include_router(auth_route.router)
api_router.include_router(user_route.router)
api_router.include_router(gig_routes.router)
api_router.include_router(chat_route.router)
api_router.include_router(buddy_routes.router)
