from app.modules.auth import auth_route
from fastapi import APIRouter
from app.modules.users import user_route

api_router = APIRouter()

api_router.include_router(auth_route.router)
api_router.include_router(user_route.router)
# api_router.include_router(file_route.router)
# api_router.include_router(gig_routes.router)
# api_router.include_router(chat_route.router)
# api_router.include_router(buddy_routes.router)
# api_router.include_router(review_routes.router)
# api_router.include_router(transaction_routes.router)
