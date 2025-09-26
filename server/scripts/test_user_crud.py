import asyncio
from app.database.session import AsyncSessionLocal
from app.models import User
from app.crud.user_crud import create_user, get_user_by_email
from app.schemas.user_schema import UserCreate
from app.security import get_password_hash

async def main():
    async with AsyncSessionLocal() as session:
        # create a unique test email using timestamp
        import time
        test_email = f"test_user_{int(time.time())}@example.com"
        user_in = UserCreate(email=test_email, password="TestPass123", full_name="Test User")
        hashed = get_password_hash(user_in.password)
        user = await create_user(session, user_in, hashed)
        print('Created user id:', user.id, 'email:', user.email)

        # fetch by email
        found = await get_user_by_email(session, test_email)
        print('Found user id:', found.id if found else None)

        # cleanup: delete the user using the ORM delete (safer in async)
        await session.delete(user)
        await session.commit()
        print('Deleted test user')

if __name__ == '__main__':
    asyncio.run(main())
