# 🚀 Chayenity API Quick Reference

> **Quick lookup for frontend developers**  
> Base URL: `http://localhost:8000/api`

## 🔐 Authentication

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login user | ❌ |
| GET | `/auth/me` | Get current user | ✅ |

## 👤 Users

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/users/profile` | Get full profile | ✅ |
| PUT | `/users/me` | Update profile | ✅ |
| PUT | `/users/location` | Set location | ✅ |
| PUT | `/users/availability` | Toggle availability | ✅ |
| GET | `/users/nearby` | Find nearby helpers | ✅ |

## 🛠️ Gigs

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/gigs/` | Create gig | ✅ |
| GET | `/gigs/search` | Search gigs | ✅ |
| GET | `/gigs/{id}` | Get gig details | ✅ |
| PUT | `/gigs/{id}` | Update gig | ✅ |
| DELETE | `/gigs/{id}` | Delete gig | ✅ |
| POST | `/gigs/{id}/accept` | Accept gig | ✅ |
| PUT | `/gigs/{id}/status` | Update status | ✅ |
| GET | `/gigs/my-gigs` | Get my gigs | ✅ |

## 💬 Chat

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/chat/rooms` | Get chat rooms | ✅ |
| GET | `/chat/rooms/{id}` | Get room details | ✅ |
| GET | `/chat/rooms/{id}/messages` | Get messages | ✅ |
| POST | `/chat/rooms/{id}/messages` | Send message | ✅ |
| PUT | `/chat/rooms/{id}/read` | Mark as read | ✅ |
| DELETE | `/chat/rooms/{id}` | Delete room | ✅ |

## 👥 Buddies

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/buddies` | Add buddy | ✅ |
| GET | `/buddies` | Get buddy list | ✅ |
| GET | `/buddies/available` | Get available buddies | ✅ |
| GET | `/buddies/{id}` | Get buddy details | ✅ |
| PUT | `/buddies/{id}` | Update buddy notes | ✅ |
| DELETE | `/buddies/{id}` | Remove buddy | ✅ |

## 📁 File Upload

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/upload/profile` | Upload profile image | ✅ |
| POST | `/upload/gig` | Upload gig image | ✅ |
| GET | `/upload/{file_id}` | Get file | ❌ |
| GET | `/upload/my-files/` | List my files | ✅ |
| DELETE | `/upload/{file_id}` | Delete file | ✅ |
| PUT | `/upload/profile/set` | Set profile image URL | ✅ |

## ⭐ Reviews

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/reviews` | Create review | ✅ |
| GET | `/reviews/user/{id}` | Get user reviews | ✅ |
| GET | `/reviews/gig/{id}` | Get gig reviews | ✅ |
| PUT | `/reviews/{id}` | Update review | ✅ |
| DELETE | `/reviews/{id}` | Delete review | ✅ |
| GET | `/reviews/my-reviews` | Get my reviews | ✅ |
| GET | `/reviews/can-review/{gig_id}/{user_id}` | Check review eligibility | ✅ |

## 💰 Transactions

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/transactions/escrow` | Create escrow | ✅ |
| PUT | `/transactions/{id}/release` | Release payment | ✅ |
| PUT | `/transactions/{id}/cancel` | Cancel transaction | ✅ |
| GET | `/transactions/{id}` | Get transaction | ✅ |
| GET | `/transactions/gig/{gig_id}` | Get gig transaction | ✅ |
| GET | `/transactions/history/my` | Get my history | ✅ |
| GET | `/transactions/summary/my` | Get payment summary | ✅ |
| POST | `/transactions/calculate-fee` | Calculate fee | ✅ |
| PUT | `/transactions/{id}/status` | Update status | ✅ |

## 🔌 WebSocket

| URL | Purpose |
|-----|---------|
| `ws://localhost:8000/ws/chat/{room_id}?token={access_token}` | Real-time chat |

### WebSocket Events
- `message` - New message received
- `user_joined` - User joined room
- `user_left` - User left room
- `typing` - Typing indicator

## 📝 Common Request Examples

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Create Gig
```bash
curl -X POST "http://localhost:8000/api/gigs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Help move furniture",
    "description": "Need help moving",
    "duration_hours": 3,
    "budget": 1500,
    "latitude": 13.7563,
    "longitude": 100.5018,
    "address_text": "123 Main St",
    "starts_at": "2025-10-01T14:00:00"
  }'
```

### Search Nearby Gigs
```bash
curl -X GET "http://localhost:8000/api/gigs/search?latitude=13.7563&longitude=100.5018&radius=5&status=PENDING" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Upload Profile Image
```bash
curl -X POST "http://localhost:8000/api/upload/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@profile.jpg"
```

### Send Chat Message
```bash
curl -X POST "http://localhost:8000/api/chat/rooms/ROOM_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello!",
    "image_url": null
  }'
```

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 415 | Unsupported Media Type |
| 422 | Validation Error |
| 500 | Server Error |

## 🛡️ Security Notes

### JWT Token Usage
```javascript
// Include in all authenticated requests
headers: {
  'Authorization': 'Bearer ' + accessToken,
  'Content-Type': 'application/json'
}
```

### File Upload Security
- Max file size: 10MB
- Allowed types: JPEG, PNG, GIF, WebP
- Files are renamed with UUID for security

### Rate Limits
- Auth endpoints: 5/min
- Upload endpoints: 10/min  
- Other endpoints: 100/min

## 🔄 Common Workflows

### User Registration Flow
1. POST `/auth/register` - Create account
2. POST `/auth/login` - Get tokens
3. PUT `/users/location` - Set location (helpers)
4. PUT `/users/availability` - Set availability

### Gig Creation Flow
1. POST `/upload/gig` - Upload images (optional)
2. POST `/gigs/` - Create gig with image URLs
3. Wait for acceptance notifications

### Gig Acceptance Flow
1. GET `/gigs/search` - Find gigs
2. POST `/gigs/{id}/accept` - Accept gig
3. Chat room automatically created
4. PUT `/gigs/{id}/status` - Update to IN_PROGRESS

### Payment Flow
1. POST `/transactions/escrow` - Create escrow when gig accepted
2. PUT `/gigs/{id}/status` - Mark as COMPLETED
3. PUT `/transactions/{id}/release` - Release payment
4. POST `/reviews` - Leave reviews

### Chat Flow
1. GET `/chat/rooms` - Get existing rooms
2. GET `/chat/rooms/{id}/messages` - Get message history
3. WebSocket connection for real-time
4. POST `/chat/rooms/{id}/messages` - Send via REST API

## 🐛 Debugging Tips

### Check API Health
```bash
curl http://localhost:8000/health
```

### Validate Token
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/ROOM_ID?token=YOUR_TOKEN');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
```

---

**Quick Reference v1.0** | Last Updated: October 1, 2025