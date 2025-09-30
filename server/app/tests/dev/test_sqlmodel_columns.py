"""
Simple test script to check SQLAlchemy table column access
"""
from app.models import ChatRoom, ChatParticipant, Message, User
from sqlmodel import select

# Test what SQLModel thinks the columns are
# Use getattr() to access __table__ at runtime so static type checkers don't complain
chatroom_table = getattr(ChatRoom, "__table__")
participant_table = getattr(ChatParticipant, "__table__")
message_table = getattr(Message, "__table__")
user_table = getattr(User, "__table__")

print("ChatRoom table name:", chatroom_table.name)
print("ChatRoom columns:", list(chatroom_table.columns.keys()))

print("\nChatParticipant table name:", participant_table.name)
print("ChatParticipant columns:", list(participant_table.columns.keys()))

print("\nMessage table name:", message_table.name)
print("Message columns:", list(message_table.columns.keys()))

print("\nUser table name:", user_table.name)
print("User columns:", list(user_table.columns.keys()))

# Test if we can create select statements
try:
    stmt1 = select(ChatRoom).where(ChatRoom.id == "test")
    print("\nChatRoom.id access works")
except Exception as e:
    print(f"\nChatRoom.id access failed: {e}")

try:
    stmt2 = select(ChatParticipant).where(ChatParticipant.user_id == "test")  
    print("ChatParticipant.user_id access works")
except Exception as e:
    print(f"ChatParticipant.user_id access failed: {e}")