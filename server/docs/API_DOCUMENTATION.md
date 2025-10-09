# 📚 Chayenity API Documentation

> **Complete API Reference for Frontend Integration**  
> Base URL: `http://localhost:8000` (Development) | `https://api.chayenity.com` (Production)

## 🔑 Authentication

All protected endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## 📖 Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [User Management](#user-management)
3. [Gig Management](#gig-management)
4. [Chat System](#chat-system)
5. [Buddy System](#buddy-system)
6. [File Upload](#file-upload)
7. [Review System](#review-system)
8. [Payment System](#payment-system)
9. [WebSocket Events](#websocket-events)
10. [Error Codes](#error-codes)

---

## 🔐 Authentication Endpoints

### Register User
**POST** `/api/auth/register`

Creates a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "contact_info": "phone:+1234567890"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "contact_info": "phone:+1234567890",
  "address_text": null,
  "is_verified": false,
  "reputation_score": 5.0,
  "created_at": "2025-10-01T10:00:00.000000"
}
```

**Errors:**
- `409 Conflict` - Email already registered

---

### Login
**POST** `/api/auth/login`

Authenticates user and returns JWT tokens.

**Request Body (Form Data):**
```
username: user@example.com (email)
password: securepassword123
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 30
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

---

### Refresh Access Token
**POST** `/api/auth/refresh`

Refreshes the access token using both refresh token and old access token for enhanced security.

**Headers:** 
```
Authorization: Bearer <refresh_token>
X-Access-Token: <old_access_token>
```

**Request Body:** None

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 30
}
```

**Security Notes:**
- Requires **both** refresh token (in Authorization header) and old access token (in X-Access-Token header)
- Validates that both tokens belong to the same user
- Accepts expired access tokens (which is normal for refresh scenarios)
- Provides enhanced security against token theft

**Errors:**
- `400 Bad Request` - Missing X-Access-Token header
- `401 Unauthorized` - Invalid tokens or token mismatch

---

### Logout
**POST** `/api/auth/logout`

Logs out the current user. In a stateless JWT system, this is mainly for client-side cleanup.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:** None

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

**Note:** For enhanced security in production, consider implementing a token blacklist.

---

### Get Current User
**GET** `/api/auth/me`

Returns current authenticated user details.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "contact_info": "phone:+1234567890",
  "address_text": "123 Main St, Bangkok",
  "is_verified": true,
  "reputation_score": 4.8,
  "created_at": "2025-10-01T10:00:00.000000"
}
```

---

## 👤 User Management

### Get User Profile
**GET** `/api/users/profile`

Returns complete user profile with location status.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "profile_image_url": "http://localhost:8000/api/upload/123e4567-e89b-12d3-a456-426614174000",
  "contact_info": "phone:+1234567890",
  "address_text": "123 Main St, Bangkok",
  "is_verified": true,
  "reputation_score": 4.8,
  "total_reviews": 25,
  "is_available": true,
  "created_at": "2025-10-01T10:00:00.000000",
  "has_location": true
}
```

---

### Update User Profile
**PUT** `/api/users/me`

Updates user profile information.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "contact_info": "phone:+1234567890,line:johnsmith",
  "address_text": "456 New Street, Bangkok"
}
```

**Response (200):** Same as Get Current User

---

### Update Location
**PUT** `/api/users/location`

Sets user's fixed location (primarily for Helpers).

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "latitude": 13.7563,
  "longitude": 100.5018,
  "address_text": "Central World, Bangkok"
}
```

**Response (200):** User object with updated location

---

### Update Availability
**PUT** `/api/users/availability`

Toggle user's availability status.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "is_available": true
}
```

**Response (200):** User object with updated availability

---

### Find Nearby Helpers
**GET** `/api/users/nearby`

Find helpers within specified radius.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `latitude` (required): Search latitude
- `longitude` (required): Search longitude  
- `radius` (optional): Search radius in km (default: 5.0)
- `only_available` (optional): Only available helpers (default: true)

**Example Request:**
```
GET /api/users/nearby?latitude=13.7563&longitude=100.5018&radius=10&only_available=true
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "Jane Helper",
    "profile_image_url": "http://localhost:8000/api/upload/helper-photo.jpg",
    "contact_info": "phone:+1234567890",
    "address_text": "Near Central World",
    "is_available": true,
    "reputation_score": 4.9,
    "total_reviews": 45,
    "distance_km": 2.3
  }
]
```

---

## 🛠️ Gig Management

### Create Gig
**POST** `/api/gigs/`

Creates a new gig request.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "title": "Help move furniture",
  "description": "Need help moving a sofa and dining table to new apartment",
  "duration_hours": 3,
  "budget": 1500.0,
  "latitude": 13.7563,
  "longitude": 100.5018,
  "address_text": "123 Main St, Bangkok",
  "starts_at": "2025-10-01T14:00:00",
  "image_urls": [
    "http://localhost:8000/api/upload/gig-photo1.jpg"
  ]
}
```

**Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Help move furniture",
  "description": "Need help moving a sofa and dining table...",
  "duration_hours": 3,
  "budget": 1500.0,
  "address_text": "123 Main St, Bangkok",
  "status": "PENDING",
  "image_urls": ["http://localhost:8000/api/upload/gig-photo1.jpg"],
  "created_at": "2025-10-01T10:00:00.000000",
  "updated_at": "2025-10-01T10:00:00.000000",
  "starts_at": "2025-10-01T14:00:00",
  "completed_at": null,
  "seeker_id": "550e8400-e29b-41d4-a716-446655440000",
  "helper_id": null,
  "latitude": null,
  "longitude": null,
  "distance_km": null
}
```

---

### Search Gigs
**GET** `/api/gigs/search`

Search for gigs with geospatial filtering.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `latitude` (required): Search center latitude
- `longitude` (required): Search center longitude
- `radius` (optional): Search radius in km (default: 10.0)
- `status` (optional): Filter by status (PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED)
- `min_budget` (optional): Minimum budget filter
- `max_budget` (optional): Maximum budget filter
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Example Request:**
```
GET /api/gigs/search?latitude=13.7563&longitude=100.5018&radius=5&status=PENDING&min_budget=500&limit=10
```

**Response (200):**
```json
{
  "gigs": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Help move furniture",
      "description": "Need help moving a sofa...",
      "duration_hours": 3,
      "budget": 1500.0,
      "address_text": "123 Main St, Bangkok",
      "status": "PENDING",
      "image_urls": ["http://localhost:8000/api/upload/gig-photo1.jpg"],
      "created_at": "2025-10-01T10:00:00.000000",
      "starts_at": "2025-10-01T14:00:00",
      "seeker_id": "550e8400-e29b-41d4-a716-446655440000",
      "helper_id": null,
      "distance_km": 2.3
    }
  ],
  "total_count": 15,
  "has_more": true
}
```

---

### Get Gig Details
**GET** `/api/gigs/{gig_id}`

Get detailed information about a specific gig.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `gig_id`: UUID of the gig

**Response (200):** Same structure as Create Gig response

**Errors:**
- `404 Not Found` - Gig not found

---

### Accept Gig
**POST** `/api/gigs/{gig_id}/accept`

Helper accepts a gig request.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `gig_id`: UUID of the gig

**Response (200):**
```json
{
  "message": "Gig accepted successfully",
  "gig": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "ACCEPTED",
    "helper_id": "helper-uuid-here",
    "updated_at": "2025-10-01T10:30:00.000000"
  }
}
```

**Errors:**
- `400 Bad Request` - Gig already accepted or not pending
- `404 Not Found` - Gig not found

---

### Update Gig Status
**PUT** `/api/gigs/{gig_id}/status`

Update gig status (start work, complete, etc.).

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `gig_id`: UUID of the gig

**Request Body:**
```json
{
  "status": "IN_PROGRESS"
}
```

**Valid Status Transitions:**
- `PENDING` → `ACCEPTED`
- `ACCEPTED` → `IN_PROGRESS`
- `IN_PROGRESS` → `COMPLETED`
- Any status → `CANCELLED`

**Response (200):** Updated gig object

---

### Get My Gigs
**GET** `/api/gigs/my-gigs`

Get user's gigs (as seeker or helper).

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `role` (optional): Filter by role ("seeker" or "helper")
- `status` (optional): Filter by status
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Example Request:**
```
GET /api/gigs/my-gigs?role=seeker&status=PENDING&limit=5
```

**Response (200):** Same structure as Search Gigs response

---

## 💬 Chat System

### Get Chat Rooms
**GET** `/api/chat/rooms`

Get user's chat rooms.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Response (200):**
```json
{
  "rooms": [
    {
      "id": "room-uuid-here",
      "gig_id": "gig-uuid-here",
      "gig_title": "Help move furniture",
      "participants": [
        {
          "id": "user1-uuid",
          "full_name": "John Seeker",
          "profile_image_url": "http://localhost:8000/api/upload/john.jpg"
        },
        {
          "id": "user2-uuid", 
          "full_name": "Jane Helper",
          "profile_image_url": "http://localhost:8000/api/upload/jane.jpg"
        }
      ],
      "last_message": "I can help you move at 2 PM",
      "last_message_at": "2025-10-01T13:30:00.000000",
      "unread_count": 2,
      "created_at": "2025-10-01T10:00:00.000000",
      "is_active": true
    }
  ],
  "total_count": 5
}
```

---

### Get Messages
**GET** `/api/chat/rooms/{room_id}/messages`

Get message history for a chat room.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `room_id`: UUID of the chat room

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Messages per page (default: 50)

**Response (200):**
```json
{
  "messages": [
    {
      "id": "msg-uuid-here",
      "content": "I can help you move at 2 PM",
      "sender_id": "user2-uuid",
      "sender_name": "Jane Helper",
      "image_url": null,
      "created_at": "2025-10-01T13:30:00.000000",
      "is_read": false
    },
    {
      "id": "msg-uuid-2",
      "content": "Perfect! See you then",
      "sender_id": "user1-uuid", 
      "sender_name": "John Seeker",
      "image_url": null,
      "created_at": "2025-10-01T13:35:00.000000",
      "is_read": true
    }
  ],
  "total_count": 8,
  "room_info": {
    "id": "room-uuid-here",
    "gig_title": "Help move furniture"
  }
}
```

---

### Send Message
**POST** `/api/chat/rooms/{room_id}/messages`

Send a message to a chat room.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `room_id`: UUID of the chat room

**Request Body:**
```json
{
  "content": "I'll be there in 10 minutes",
  "image_url": null
}
```

**Response (201):**
```json
{
  "id": "new-msg-uuid",
  "content": "I'll be there in 10 minutes",
  "sender_id": "current-user-uuid",
  "sender_name": "Current User",
  "image_url": null,
  "created_at": "2025-10-01T14:00:00.000000",
  "is_read": false
}
```

---

### Mark Messages as Read
**PUT** `/api/chat/rooms/{room_id}/read`

Mark all messages in a room as read.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `room_id`: UUID of the chat room

**Response (200):**
```json
{
  "message": "Messages marked as read",
  "updated_count": 3
}
```

---

## 👥 Buddy System

### Add Buddy
**POST** `/api/buddies`

Add a user to buddy/favorites list.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "buddy_user_id": "buddy-uuid-here",
  "notes": "Great helper, very reliable"
}
```

**Response (201):**
```json
{
  "id": "buddy-relationship-uuid",
  "buddy_user_id": "buddy-uuid-here",
  "notes": "Great helper, very reliable",
  "created_at": "2025-10-01T10:00:00.000000",
  "buddy_info": {
    "id": "buddy-uuid-here",
    "full_name": "Jane Helper",
    "profile_image_url": "http://localhost:8000/api/upload/jane.jpg",
    "reputation_score": 4.8,
    "total_reviews": 45
  }
}
```

---

### Get Buddies
**GET** `/api/buddies`

Get user's buddy list.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Response (200):**
```json
{
  "buddies": [
    {
      "id": "buddy-relationship-uuid",
      "buddy_user_id": "buddy-uuid-here",
      "notes": "Great helper, very reliable",
      "created_at": "2025-10-01T10:00:00.000000",
      "buddy_info": {
        "id": "buddy-uuid-here",
        "full_name": "Jane Helper",
        "profile_image_url": "http://localhost:8000/api/upload/jane.jpg",
        "reputation_score": 4.8,
        "total_reviews": 45,
        "is_available": true
      }
    }
  ],
  "total_count": 3
}
```

---

### Get Available Buddies
**GET** `/api/buddies/available`

Get only available buddies.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):** Same structure as Get Buddies, filtered for available users

---

### Remove Buddy
**DELETE** `/api/buddies/{buddy_id}`

Remove a buddy from favorites list.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `buddy_id`: UUID of the buddy relationship

**Response (204):** No content

---

## 📁 File Upload

### Upload Profile Image
**POST** `/api/upload/profile`

Upload a profile image.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body (Multipart/Form-Data):**
```
file: [image file] (JPEG, PNG, GIF, WebP)
```

**Response (201):**
```json
{
  "file_id": "file-uuid-here",
  "filename": "abc123-profile.jpg",
  "original_filename": "my-photo.jpg",
  "file_size": 245760,
  "content_type": "image/jpeg",
  "url": "http://localhost:8000/api/upload/file-uuid-here",
  "uploaded_at": "2025-10-01T10:00:00.000000"
}
```

**File Constraints:**
- Max size: 10MB
- Allowed types: JPEG, PNG, GIF, WebP

---

### Upload Gig Image
**POST** `/api/upload/gig`

Upload images for gigs.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body (Multipart/Form-Data):**
```
file: [image file]
```

**Response (201):** Same structure as Upload Profile Image

---

### Get Uploaded File
**GET** `/api/upload/{file_id}`

Serve an uploaded file.

**Path Parameters:**
- `file_id`: UUID of the file

**Response (200):** File content with appropriate Content-Type header

**Errors:**
- `404 Not Found` - File not found

---

### List My Files
**GET** `/api/upload/my-files/`

Get user's uploaded files.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `category` (optional): Filter by category ("profile", "gig", "general")
- `limit` (optional): Results per page (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
[
  {
    "file_id": "file-uuid-here",
    "filename": "abc123-profile.jpg",
    "original_filename": "my-photo.jpg",
    "file_size": 245760,
    "content_type": "image/jpeg",
    "category": "profile",
    "uploaded_at": "2025-10-01T10:00:00.000000"
  }
]
```

---

### Delete File
**DELETE** `/api/upload/{file_id}`

Delete an uploaded file.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `file_id`: UUID of the file

**Response (204):** No content

**Errors:**
- `404 Not Found` - File not found
- `403 Forbidden` - Not file owner

---

## ⭐ Review System

### Create Review
**POST** `/api/reviews`

Create a review after gig completion.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "gig_id": "gig-uuid-here",
  "reviewee_id": "user-uuid-to-review",
  "rating": 5,
  "comment": "Excellent work! Very professional and on time."
}
```

**Response (201):**
```json
{
  "id": "review-uuid-here",
  "gig_id": "gig-uuid-here",
  "reviewer_id": "current-user-uuid",
  "reviewee_id": "user-uuid-reviewed",
  "rating": 5,
  "comment": "Excellent work! Very professional and on time.",
  "created_at": "2025-10-01T15:00:00.000000",
  "updated_at": "2025-10-01T15:00:00.000000",
  "reviewer_name": "John Seeker",
  "reviewee_name": "Jane Helper",
  "gig_title": "Help move furniture"
}
```

**Constraints:**
- Rating: 1-5 stars
- Comment: Required, max 1000 characters
- Can only review after gig completion
- One review per user per gig

---

### Get User Reviews
**GET** `/api/reviews/user/{user_id}`

Get reviews for a specific user.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `user_id`: UUID of the user

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Response (200):**
```json
{
  "reviews": [
    {
      "id": "review-uuid-here",
      "rating": 5,
      "comment": "Excellent work! Very professional and on time.",
      "created_at": "2025-10-01T15:00:00.000000",
      "reviewer_name": "John Seeker",
      "gig_title": "Help move furniture"
    }
  ],
  "total_count": 25,
  "average_rating": 4.8,
  "rating_distribution": {
    "5": 20,
    "4": 3,
    "3": 2,
    "2": 0,
    "1": 0
  }
}
```

---

### Get My Reviews
**GET** `/api/reviews/my-reviews`

Get reviews written by current user.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)  
- `limit` (optional): Results per page (default: 20)

**Response (200):** Same structure as Get User Reviews

---

### Update Review
**PUT** `/api/reviews/{review_id}`

Update a review (author only).

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `review_id`: UUID of the review

**Request Body:**
```json
{
  "rating": 4,
  "comment": "Good work, but arrived 15 minutes late."
}
```

**Response (200):** Updated review object

**Errors:**
- `403 Forbidden` - Not review author
- `404 Not Found` - Review not found

---

### Delete Review
**DELETE** `/api/reviews/{review_id}`

Delete a review (author only).

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `review_id`: UUID of the review

**Response (204):** No content

---

## 💰 Payment System

### Create Escrow
**POST** `/api/transactions/escrow`

Create escrow transaction (hold payment).

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "gig_id": "gig-uuid-here",
  "payment_method": "mock_payment"
}
```

**Response (201):**
```json
{
  "id": "transaction-uuid-here",
  "gig_id": "gig-uuid-here",
  "payer_id": "seeker-uuid",
  "payee_id": "helper-uuid",
  "amount": 1500.0,
  "service_fee": 75.0,
  "net_amount": 1425.0,
  "currency": "THB",
  "status": "PENDING",
  "payment_method": "mock_payment",
  "transaction_ref": "TXN-2025100115001",
  "created_at": "2025-10-01T15:00:00.000000",
  "completed_at": null,
  "gig_title": "Help move furniture",
  "payer_name": "John Seeker",
  "payee_name": "Jane Helper"
}
```

---

### Release Payment
**PUT** `/api/transactions/{transaction_id}/release`

Release payment from escrow to helper.

**Headers:** `Authorization: Bearer <access_token>`

**Path Parameters:**
- `transaction_id`: UUID of the transaction

**Request Body:**
```json
{
  "release_reason": "Gig completed successfully"
}
```

**Response (200):**
```json
{
  "message": "Payment released successfully",
  "transaction": {
    "id": "transaction-uuid-here",
    "status": "COMPLETED",
    "completed_at": "2025-10-01T17:00:00.000000",
    "net_amount": 1425.0
  }
}
```

---

### Get Transaction History
**GET** `/api/transactions/history/my`

Get user's transaction history.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 20)

**Response (200):**
```json
{
  "transactions": [
    {
      "id": "transaction-uuid-here",
      "gig_id": "gig-uuid-here",
      "amount": 1500.0,
      "service_fee": 75.0,
      "net_amount": 1425.0,
      "currency": "THB",
      "status": "COMPLETED",
      "created_at": "2025-10-01T15:00:00.000000",
      "completed_at": "2025-10-01T17:00:00.000000",
      "gig_title": "Help move furniture",
      "payer_name": "John Seeker",
      "payee_name": "Jane Helper"
    }
  ],
  "total_count": 10,
  "total_paid": 7500.0,
  "total_received": 3400.0,
  "currency": "THB"
}
```

---

### Calculate Service Fee
**POST** `/api/transactions/calculate-fee`

Calculate service fee for a given amount.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "base_amount": 1500.0
}
```

**Response (200):**
```json
{
  "base_amount": 1500.0,
  "service_fee_rate": 0.05,
  "service_fee_amount": 75.0,
  "net_amount": 1425.0,
  "currency": "THB"
}
```

---

## 🔌 WebSocket Events

### Connection
**WebSocket URL:** `ws://localhost:8000/ws/chat/{room_id}?token={access_token}`

### Event Types

#### Message Received
```json
{
  "type": "message",
  "data": {
    "id": "msg-uuid-here",
    "content": "Hello from WebSocket!",
    "sender_id": "user-uuid",
    "sender_name": "Jane Helper",
    "image_url": null,
    "created_at": "2025-10-01T14:00:00.000000"
  }
}
```

#### User Joined
```json
{
  "type": "user_joined",
  "data": {
    "user_id": "user-uuid",
    "user_name": "John Seeker",
    "timestamp": "2025-10-01T14:00:00.000000"
  }
}
```

#### User Left
```json
{
  "type": "user_left", 
  "data": {
    "user_id": "user-uuid",
    "user_name": "John Seeker", 
    "timestamp": "2025-10-01T14:30:00.000000"
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "data": {
    "user_id": "user-uuid",
    "user_name": "Jane Helper",
    "is_typing": true
  }
}
```

### Sending Messages via WebSocket
```json
{
  "type": "send_message",
  "content": "Hello via WebSocket!",
  "image_url": null
}
```

---

## ⚠️ Error Codes

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Invalid request data, missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., email taken) |
| 415 | Unsupported Media Type | Invalid file type upload |
| 422 | Validation Error | Pydantic validation failed |
| 500 | Internal Server Error | Server-side error |

### Error Response Format
```json
{
  "detail": "Error message here",
  "error_code": "SPECIFIC_ERROR_CODE",
  "field_errors": {
    "email": ["Invalid email format"],
    "password": ["Password too short"]
  }
}
```

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `EMAIL_ALREADY_EXISTS` | Email already registered |
| `INVALID_CREDENTIALS` | Wrong email/password |
| `TOKEN_EXPIRED` | JWT token expired |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `GIG_ALREADY_ACCEPTED` | Gig already has a helper |
| `INVALID_STATUS_TRANSITION` | Invalid gig status change |
| `REVIEW_ALREADY_EXISTS` | User already reviewed this gig |
| `TRANSACTION_NOT_PENDING` | Transaction not in correct status |
| `FILE_TOO_LARGE` | Uploaded file exceeds size limit |
| `INVALID_FILE_TYPE` | File type not supported |

---

## 📱 Frontend Integration Examples

### React/TypeScript Example

```typescript
// api.ts
const API_BASE = 'http://localhost:8000/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiClient {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }
    
    return headers;
  }

  async login(email: string, password: string): Promise<ApiResponse<LoginResponse>> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      // Store refresh token securely (e.g., secure cookie or encrypted storage)
      localStorage.setItem('refresh_token', data.refresh_token);
      return { data };
    } else {
      const error = await response.json();
      return { error: error.detail };
    }
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.accessToken || !this.refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.refreshToken}`,
          'X-Access-Token': this.accessToken,
        },
      });

      if (response.ok) {
        const data = await response.json();
        this.accessToken = data.access_token;
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    
    return false;
  }

  async secureApiCall<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    let response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    // If 401, try to refresh tokens and retry
    if (response.status === 401) {
      const refreshSuccess = await this.refreshAccessToken();
      
      if (refreshSuccess) {
        // Retry with new access token
        response = await fetch(url, {
          ...options,
          headers: {
            ...this.getHeaders(),
            ...options.headers,
          },
        });
      } else {
        // Refresh failed, redirect to login
        this.logout();
        return { error: 'Session expired. Please login again.' };
      }
    }

    if (response.ok) {
      const data = await response.json();
      return { data };
    } else {
      const error = await response.json();
      return { error: error.detail };
    }
  }

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      // Always clear tokens locally
      this.accessToken = null;
      this.refreshToken = null;
      localStorage.removeItem('refresh_token');
      // Redirect to login page
      window.location.href = '/login';
    }
  }

  async createGig(gigData: CreateGigRequest): Promise<ApiResponse<Gig>> {
    return this.secureApiCall(`${API_BASE}/gigs/`, {
      method: 'POST',
      body: JSON.stringify(gigData),
    });
  }

  async uploadProfileImage(file: File): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.secureApiCall(`${API_BASE}/upload/profile`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
      body: formData,
    });
  }
}

// Usage
const api = new ApiClient();

// Login with automatic token storage
const loginResult = await api.login('user@example.com', 'password');
if (loginResult.data) {
  console.log('Logged in successfully');
}

// All API calls now have automatic token refresh
const gigResult = await api.createGig({
  title: 'Help move furniture',
  description: 'Need help moving',
  duration_hours: 3,
  budget: 1500,
  latitude: 13.7563,
  longitude: 100.5018,
  address_text: '123 Main St',
  starts_at: '2025-10-01T14:00:00'
});
```

### Flutter/Dart Example

```dart
// api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  String? _accessToken;
  String? _refreshToken;
  
  void setTokens(String accessToken, String refreshToken) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
  }
  
  Map<String, String> get _headers {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    
    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    
    return headers;
  }
  
  Future<ApiResult<LoginResponse>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,
          'password': password,
        },
      );
      
      if (response.statusCode == 200) {
        final data = LoginResponse.fromJson(jsonDecode(response.body));
        setTokens(data.accessToken, data.refreshToken);
        
        // Store refresh token securely
        await _secureStorage.write(key: 'refresh_token', value: data.refreshToken);
        
        return ApiResult.success(data);
      } else {
        final error = jsonDecode(response.body);
        return ApiResult.error(error['detail']);
      }
    } catch (e) {
      return ApiResult.error(e.toString());
    }
  }
  
  Future<bool> _refreshAccessToken() async {
    if (_accessToken == null || _refreshToken == null) {
      return false;
    }
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {
          'Authorization': 'Bearer $_refreshToken',
          'X-Access-Token': _accessToken!,
        },
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _accessToken = data['access_token'];
        return true;
      }
    } catch (e) {
      print('Token refresh failed: $e');
    }
    
    return false;
  }
  
  Future<ApiResult<T>> _secureApiCall<T>(
    String endpoint,
    T Function(Map<String, dynamic>) fromJson, {
    String method = 'GET',
    Map<String, dynamic>? body,
    Map<String, String>? additionalHeaders,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = {..._headers, ...?additionalHeaders};
    
    http.Response response;
    
    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(uri, headers: headers);
        break;
      case 'POST':
        response = await http.post(
          uri,
          headers: headers,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'PUT':
        response = await http.put(
          uri,
          headers: headers,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'DELETE':
        response = await http.delete(uri, headers: headers);
        break;
      default:
        throw ArgumentError('Unsupported HTTP method: $method');
    }
    
    // Handle 401 with token refresh
    if (response.statusCode == 401) {
      final refreshSuccess = await _refreshAccessToken();
      
      if (refreshSuccess) {
        // Retry with new access token
        final newHeaders = {..._headers, ...?additionalHeaders};
        
        switch (method.toUpperCase()) {
          case 'GET':
            response = await http.get(uri, headers: newHeaders);
            break;
          case 'POST':
            response = await http.post(
              uri,
              headers: newHeaders,
              body: body != null ? jsonEncode(body) : null,
            );
            break;
          case 'PUT':
            response = await http.put(
              uri,
              headers: newHeaders,
              body: body != null ? jsonEncode(body) : null,
            );
            break;
          case 'DELETE':
            response = await http.delete(uri, headers: newHeaders);
            break;
        }
      } else {
        // Refresh failed, logout
        await logout();
        return ApiResult.error('Session expired. Please login again.');
      }
    }
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = fromJson(jsonDecode(response.body));
      return ApiResult.success(data);
    } else {
      final error = jsonDecode(response.body);
      return ApiResult.error(error['detail'] ?? 'Unknown error');
    }
  }
  
  Future<void> logout() async {
    try {
      await http.post(
        Uri.parse('$baseUrl/auth/logout'),
        headers: _headers,
      );
    } catch (e) {
      print('Logout request failed: $e');
    } finally {
      // Always clear tokens
      _accessToken = null;
      _refreshToken = null;
      await _secureStorage.delete(key: 'refresh_token');
      // Navigate to login screen
      // Navigator.of(context).pushReplacementNamed('/login');
    }
  }
  
  Future<ApiResult<List<Gig>>> searchGigs({
    required double latitude,
    required double longitude,
    double radius = 10.0,
    String? status,
  }) async {
    final queryParams = {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'radius': radius.toString(),
      if (status != null) 'status': status,
    };
    
    final uri = Uri.parse('$baseUrl/gigs/search').replace(
      queryParameters: queryParams,
    );
    
    return _secureApiCall(
      uri.toString().replaceFirst(baseUrl, ''),
      (json) => (json['gigs'] as List)
          .map((gigJson) => Gig.fromJson(gigJson))
          .toList(),
    );
  }
  
  Future<ApiResult<Gig>> createGig(CreateGigRequest gigData) async {
    return _secureApiCall(
      '/gigs/',
      (json) => Gig.fromJson(json),
      method: 'POST',
      body: gigData.toJson(),
    );
  }
}

// Usage
final apiService = ApiService();

// Login with automatic token storage
final loginResult = await apiService.login('user@example.com', 'password');
loginResult.when(
  success: (data) => print('Logged in successfully'),
  error: (error) => print('Login failed: $error'),
);

// All API calls now have automatic token refresh
final gigsResult = await apiService.searchGigs(
  latitude: 13.7563,
  longitude: 100.5018,
  radius: 5.0,
  status: 'PENDING',
);
gigsResult.when(
  success: (gigs) => print('Found ${gigs.length} gigs'),
  error: (error) => print('Search failed: $error'),
);

// Create gig with automatic token management
final createResult = await apiService.createGig(CreateGigRequest(
  title: 'Help move furniture',
  description: 'Need help moving',
  durationHours: 3,
  budget: 1500,
  latitude: 13.7563,
  longitude: 100.5018,
  addressText: '123 Main St',
  startsAt: DateTime.now().add(Duration(hours: 4)),
));
```

---

## 🔧 Development Notes

### Base URL Configuration
- **Development:** `http://localhost:8000`
- **Staging:** `https://api-staging.chayenity.com`
- **Production:** `https://api.chayenity.com`

### Rate Limiting
- Authentication endpoints: 5 requests per minute
- File upload endpoints: 10 requests per minute
- Other endpoints: 100 requests per minute

### File Upload Limits
- Profile images: 10MB max
- Gig images: 10MB max
- Supported formats: JPEG, PNG, GIF, WebP

### WebSocket Connection
- Auto-reconnection recommended
- Heartbeat every 30 seconds
- Token refresh handling required

### Pagination
- Default page size: 20 items
- Maximum page size: 100 items
- Use `skip` and `limit` parameters

### Date Formats
- All timestamps in ISO 8601 format with timezone
- Example: `2025-10-01T14:00:00.000000`
- Timezone: UTC

---

**Last Updated:** October 1, 2025  
**API Version:** 1.0.0  
**Documentation Version:** 1.0.0