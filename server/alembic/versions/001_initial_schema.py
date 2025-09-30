"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-10-01 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create User table
    op.create_table('user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.VARCHAR(), nullable=False),
        sa.Column('hashed_password', sa.VARCHAR(), nullable=False),
        sa.Column('full_name', sa.VARCHAR(), nullable=False),
        sa.Column('profile_image_url', sa.VARCHAR(), nullable=True),
        sa.Column('contact_info', sa.VARCHAR(), nullable=True),
        sa.Column('fixed_location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('address_text', sa.VARCHAR(), nullable=True),
        sa.Column('is_available', sa.BOOLEAN(), nullable=False, default=False),
        sa.Column('is_verified', sa.BOOLEAN(), nullable=False, default=False),
        sa.Column('reputation_score', sa.FLOAT(), nullable=False, default=5.0),
        sa.Column('total_reviews', sa.INTEGER(), nullable=False, default=0),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    # Skip spatial index for now - PostGIS handles it automatically

    # Create BuddyList table
    op.create_table('buddylist',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('buddy_id', sa.UUID(), nullable=False),
        sa.Column('notes', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['buddy_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_buddylist_buddy_id', 'buddylist', ['buddy_id'])
    op.create_index('ix_buddylist_user_id', 'buddylist', ['user_id'])

    # Create Gig table
    op.create_table('gig',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.Column('description', sa.VARCHAR(), nullable=False),
        sa.Column('budget', sa.NUMERIC(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.VARCHAR(), nullable=False, default='THB'),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('address_text', sa.VARCHAR(), nullable=False),
        sa.Column('estimated_duration_hours', sa.FLOAT(), nullable=True),
        sa.Column('status', sa.VARCHAR(), nullable=False, default='pending'),
        sa.Column('seeker_id', sa.UUID(), nullable=False),
        sa.Column('helper_id', sa.UUID(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['helper_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['seeker_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gig_budget', 'gig', ['budget'])
    op.create_index('ix_gig_created_at', 'gig', ['created_at'])
    op.create_index('ix_gig_helper_id', 'gig', ['helper_id'])
    op.create_index('ix_gig_seeker_id', 'gig', ['seeker_id'])
    op.create_index('ix_gig_status', 'gig', ['status'])
    op.create_index('ix_gig_title', 'gig', ['title'])
    # Skip spatial index for gig location - PostGIS handles it automatically

    # Create UploadedFile table
    op.create_table('uploadedfile',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('filename', sa.VARCHAR(), nullable=False),
        sa.Column('original_filename', sa.VARCHAR(), nullable=False),
        sa.Column('file_path', sa.VARCHAR(), nullable=False),
        sa.Column('file_size', sa.INTEGER(), nullable=False),
        sa.Column('content_type', sa.VARCHAR(), nullable=False),
        sa.Column('upload_category', sa.VARCHAR(), nullable=False),
        sa.Column('uploaded_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), nullable=False, default=True),
        sa.Column('uploaded_by', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['uploaded_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_uploadedfile_filename', 'uploadedfile', ['filename'])
    op.create_index('ix_uploadedfile_is_active', 'uploadedfile', ['is_active'])
    op.create_index('ix_uploadedfile_upload_category', 'uploadedfile', ['upload_category'])
    op.create_index('ix_uploadedfile_uploaded_at', 'uploadedfile', ['uploaded_at'])
    op.create_index('ix_uploadedfile_uploaded_by', 'uploadedfile', ['uploaded_by'])

    # Create ChatRoom table
    op.create_table('chatroom',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gig_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['gig_id'], ['gig.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chatroom_gig_id', 'chatroom', ['gig_id'])

    # Create Review table  
    op.create_table('review',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gig_id', sa.UUID(), nullable=False),
        sa.Column('reviewer_id', sa.UUID(), nullable=False),
        sa.Column('reviewee_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.INTEGER(), nullable=False),
        sa.Column('comment', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['gig_id'], ['gig.id'], ),
        sa.ForeignKeyConstraint(['reviewee_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_review_gig_id', 'review', ['gig_id'])

    # Create Transaction table
    op.create_table('transaction',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('gig_id', sa.UUID(), nullable=False),
        sa.Column('payer_id', sa.UUID(), nullable=False),
        sa.Column('payee_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.NUMERIC(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.VARCHAR(), nullable=False, default='THB'),
        sa.Column('status', sa.VARCHAR(), nullable=False, default='pending'),
        sa.Column('payment_method', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['gig_id'], ['gig.id'], ),
        sa.ForeignKeyConstraint(['payee_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['payer_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transaction_gig_id', 'transaction', ['gig_id'])
    op.create_index('ix_transaction_payee_id', 'transaction', ['payee_id'])
    op.create_index('ix_transaction_payer_id', 'transaction', ['payer_id'])
    op.create_index('ix_transaction_status', 'transaction', ['status'])

    # Create ChatParticipant table
    op.create_table('chatparticipant',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('chat_room_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('joined_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['chat_room_id'], ['chatroom.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chatparticipant_chat_room_id', 'chatparticipant', ['chat_room_id'])
    op.create_index('ix_chatparticipant_user_id', 'chatparticipant', ['user_id'])

    # Create Message table
    op.create_table('message',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('chat_room_id', sa.UUID(), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.VARCHAR(), nullable=False),
        sa.Column('message_type', sa.VARCHAR(), nullable=False, default='text'),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_read', sa.BOOLEAN(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['chat_room_id'], ['chatroom.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_message_chat_room_id', 'message', ['chat_room_id'])
    op.create_index('ix_message_is_read', 'message', ['is_read'])
    op.create_index('ix_message_sender_id', 'message', ['sender_id'])
    op.create_index('ix_message_timestamp', 'message', ['timestamp'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('message')
    op.drop_table('chatparticipant')
    op.drop_table('transaction')
    op.drop_table('review')
    op.drop_table('chatroom')
    op.drop_table('uploadedfile')
    op.drop_table('gig')
    op.drop_table('buddylist')
    op.drop_table('user')