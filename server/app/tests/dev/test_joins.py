"""
Test SQLModel join syntax
"""
from sqlmodel import select
from app.models import ChatRoom, ChatParticipant, User

# Test different join approaches
print("Testing SQLModel join syntax...")

try:
    # Approach 1: SQLModel automatic join
    stmt1 = select(ChatRoom).join(ChatParticipant).where(ChatParticipant.user_id == "test")
    print("✅ Basic join works")
except Exception as e:
    print(f"❌ Basic join failed: {e}")

try:
    # Approach 2: Explicit join condition 
    # Use getattr to access __table__ at runtime so static analyzers don't complain
    chatroom_table = getattr(ChatRoom, "__table__")
    participant_table = getattr(ChatParticipant, "__table__")
    stmt2 = select(ChatRoom).join(
        ChatParticipant,
        chatroom_table.c.id == participant_table.c.chat_room_id,
    )
    print("✅ Explicit join works")
except Exception as e:
    print(f"❌ Explicit join failed: {e}")

try:
    # Approach 3: Manual where with multiple tables
    stmt3 = select(ChatRoom).where(
        ChatRoom.id == ChatParticipant.chat_room_id,
        ChatParticipant.user_id == "test"
    )
    print("✅ Manual where works")
except Exception as e:
    print(f"❌ Manual where failed: {e}")

print("Test complete!")