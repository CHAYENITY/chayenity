# 📱 Frontend Integration Guide - Chayenity API

> **Ready-to-use code examples for frontend developers**

## 🎯 JavaScript/TypeScript Integration

### API Client Setup

```typescript
// src/services/api.ts
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  statusCode?: number;
}

export class ChayenityApi {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000/api') {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('chayenity_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('chayenity_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('chayenity_token');
  }

  private getHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      if (response.ok) {
        const data = await response.json();
        return { data, statusCode: response.status };
      } else {
        const errorData = await response.json();
        return { 
          error: errorData.detail || 'An error occurred', 
          statusCode: response.status 
        };
      }
    } catch (error) {
      return { 
        error: 'Network error or invalid response', 
        statusCode: response.status 
      };
    }
  }

  // Authentication Methods
  async login(email: string, password: string): Promise<ApiResponse<LoginResponse>> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    const result = await this.handleResponse<LoginResponse>(response);
    if (result.data) {
      this.setToken(result.data.access_token);
    }
    return result;
  }

  async register(userData: RegisterRequest): Promise<ApiResponse<User>> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(false),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<User>(response);
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    const response = await fetch(`${this.baseUrl}/auth/me`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<User>(response);
  }

  // Gig Methods
  async createGig(gigData: CreateGigRequest): Promise<ApiResponse<Gig>> {
    const response = await fetch(`${this.baseUrl}/gigs/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(gigData),
    });

    return this.handleResponse<Gig>(response);
  }

  async searchGigs(params: GigSearchParams): Promise<ApiResponse<GigListResponse>> {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });

    const response = await fetch(`${this.baseUrl}/gigs/search?${queryParams}`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<GigListResponse>(response);
  }

  async acceptGig(gigId: string): Promise<ApiResponse<{ message: string; gig: Gig }>> {
    const response = await fetch(`${this.baseUrl}/gigs/${gigId}/accept`, {
      method: 'POST',
      headers: this.getHeaders(),
    });

    return this.handleResponse(response);
  }

  // File Upload Methods
  async uploadProfileImage(file: File): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload/profile`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
      body: formData,
    });

    return this.handleResponse<FileUploadResponse>(response);
  }

  // Chat Methods
  async getChatRooms(params?: PaginationParams): Promise<ApiResponse<ChatRoomsResponse>> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const response = await fetch(`${this.baseUrl}/chat/rooms?${queryParams}`, {
      headers: this.getHeaders(),
    });

    return this.handleResponse<ChatRoomsResponse>(response);
  }

  async sendMessage(roomId: string, content: string, imageUrl?: string): Promise<ApiResponse<Message>> {
    const response = await fetch(`${this.baseUrl}/chat/rooms/${roomId}/messages`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ content, image_url: imageUrl }),
    });

    return this.handleResponse<Message>(response);
  }

  // WebSocket connection helper
  createChatWebSocket(roomId: string): WebSocket {
    const token = this.getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }

    const wsUrl = `ws://localhost:8000/ws/chat/${roomId}?token=${token}`;
    return new WebSocket(wsUrl);
  }
}

// Type definitions
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in_minutes: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  contact_info?: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  profile_image_url?: string;
  contact_info?: string;
  address_text?: string;
  is_verified: boolean;
  reputation_score: number;
  total_reviews?: number;
  is_available?: boolean;
  created_at: string;
}

export interface CreateGigRequest {
  title: string;
  description: string;
  duration_hours: number;
  budget: number;
  latitude: number;
  longitude: number;
  address_text: string;
  starts_at: string;
  image_urls?: string[];
}

export interface Gig {
  id: string;
  title: string;
  description: string;
  duration_hours: number;
  budget: number;
  address_text: string;
  status: 'PENDING' | 'ACCEPTED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  image_urls: string[];
  created_at: string;
  updated_at: string;
  starts_at: string;
  completed_at?: string;
  seeker_id: string;
  helper_id?: string;
  distance_km?: number;
}

export interface GigSearchParams {
  latitude: number;
  longitude: number;
  radius?: number;
  status?: string;
  min_budget?: number;
  max_budget?: number;
  skip?: number;
  limit?: number;
}

export interface GigListResponse {
  gigs: Gig[];
  total_count: number;
  has_more: boolean;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ChatRoomsResponse {
  rooms: ChatRoom[];
  total_count: number;
}

export interface ChatRoom {
  id: string;
  gig_id: string;
  gig_title: string;
  participants: User[];
  last_message: string;
  last_message_at: string;
  unread_count: number;
  created_at: string;
  is_active: boolean;
}

export interface Message {
  id: string;
  content: string;
  sender_id: string;
  sender_name: string;
  image_url?: string;
  created_at: string;
  is_read: boolean;
}

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  url: string;
  uploaded_at: string;
}
```

### Usage Examples

```typescript
// src/services/chayenity.ts
import { ChayenityApi } from './api';

const api = new ChayenityApi();

// Login example
export async function loginUser(email: string, password: string) {
  const result = await api.login(email, password);
  
  if (result.error) {
    throw new Error(result.error);
  }
  
  return result.data!;
}

// Create gig example
export async function createNewGig(gigData: CreateGigRequest) {
  const result = await api.createGig(gigData);
  
  if (result.error) {
    throw new Error(result.error);
  }
  
  return result.data!;
}

// Search gigs example
export async function findNearbyGigs(
  latitude: number, 
  longitude: number, 
  radius: number = 10
) {
  const result = await api.searchGigs({
    latitude,
    longitude,
    radius,
    status: 'PENDING',
    limit: 20
  });
  
  if (result.error) {
    throw new Error(result.error);
  }
  
  return result.data!;
}

// Upload profile image example
export async function uploadUserProfileImage(file: File) {
  const result = await api.uploadProfileImage(file);
  
  if (result.error) {
    throw new Error(result.error);
  }
  
  return result.data!;
}
```

## 🔌 WebSocket Chat Integration

```typescript
// src/services/chatWebSocket.ts
import { ChayenityApi } from './api';

export interface WebSocketMessage {
  type: 'message' | 'user_joined' | 'user_left' | 'typing';
  data: any;
}

export class ChatWebSocketManager {
  private ws: WebSocket | null = null;
  private api: ChayenityApi;
  private roomId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private onMessageCallback?: (message: WebSocketMessage) => void;
  private onConnectCallback?: () => void;
  private onDisconnectCallback?: () => void;

  constructor(api: ChayenityApi, roomId: string) {
    this.api = api;
    this.roomId = roomId;
  }

  connect() {
    try {
      this.ws = this.api.createChatWebSocket(this.roomId);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.onConnectCallback?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.onMessageCallback?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.onDisconnectCallback?.();
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  sendMessage(content: string, imageUrl?: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'send_message',
        content,
        image_url: imageUrl
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
    }
  }

  sendTypingIndicator(isTyping: boolean) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'typing',
        is_typing: isTyping
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  onMessage(callback: (message: WebSocketMessage) => void) {
    this.onMessageCallback = callback;
  }

  onConnect(callback: () => void) {
    this.onConnectCallback = callback;
  }

  onDisconnect(callback: () => void) {
    this.onDisconnectCallback = callback;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Usage example
export function useChatWebSocket(api: ChayenityApi, roomId: string) {
  const chatWS = new ChatWebSocketManager(api, roomId);
  
  chatWS.onMessage((message) => {
    switch (message.type) {
      case 'message':
        console.log('New message:', message.data);
        // Update UI with new message
        break;
      case 'user_joined':
        console.log('User joined:', message.data.user_name);
        break;
      case 'user_left':
        console.log('User left:', message.data.user_name);
        break;
      case 'typing':
        console.log('Typing indicator:', message.data);
        break;
    }
  });

  chatWS.onConnect(() => {
    console.log('Chat connected successfully');
  });

  chatWS.onDisconnect(() => {
    console.log('Chat disconnected');
  });

  return chatWS;
}
```

## 🎯 React Hook Examples

```typescript
// src/hooks/useChayenityApi.ts
import { useState, useEffect } from 'react';
import { ChayenityApi, User, Gig } from '../services/api';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const api = new ChayenityApi();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = api.getToken();
      if (token) {
        const result = await api.getCurrentUser();
        if (result.data) {
          setUser(result.data);
        } else {
          api.clearToken();
        }
      }
    } catch (err) {
      setError('Failed to check authentication status');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.login(email, password);
      if (result.data) {
        const userResult = await api.getCurrentUser();
        if (userResult.data) {
          setUser(userResult.data);
        }
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError('Login failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.clearToken();
    setUser(null);
  };

  return { user, login, logout, loading, error };
}

export function useGigs() {
  const [gigs, setGigs] = useState<Gig[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const api = new ChayenityApi();

  const searchGigs = async (latitude: number, longitude: number, radius: number = 10) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.searchGigs({
        latitude,
        longitude,
        radius,
        status: 'PENDING',
        limit: 20
      });
      
      if (result.data) {
        setGigs(result.data.gigs);
      } else {
        setError(result.error || 'Failed to search gigs');
      }
    } catch (err) {
      setError('Failed to search gigs');
    } finally {
      setLoading(false);
    }
  };

  const createGig = async (gigData: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.createGig(gigData);
      if (result.data) {
        setGigs(prev => [result.data!, ...prev]);
        return result.data;
      } else {
        setError(result.error || 'Failed to create gig');
        return null;
      }
    } catch (err) {
      setError('Failed to create gig');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { gigs, searchGigs, createGig, loading, error };
}
```

## 📱 React Component Examples

```tsx
// src/components/LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../hooks/useChayenityApi';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// src/components/GigList.tsx
import React, { useEffect } from 'react';
import { useGigs } from '../hooks/useChayenityApi';

interface GigListProps {
  latitude: number;
  longitude: number;
}

export function GigList({ latitude, longitude }: GigListProps) {
  const { gigs, searchGigs, loading, error } = useGigs();

  useEffect(() => {
    searchGigs(latitude, longitude, 10);
  }, [latitude, longitude]);

  if (loading) return <div>Loading gigs...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Nearby Gigs</h2>
      {gigs.map(gig => (
        <div key={gig.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
          <h3>{gig.title}</h3>
          <p>{gig.description}</p>
          <p>Budget: ฿{gig.budget}</p>
          <p>Duration: {gig.duration_hours} hours</p>
          <p>Status: {gig.status}</p>
          {gig.distance_km && <p>Distance: {gig.distance_km.toFixed(1)} km</p>}
        </div>
      ))}
    </div>
  );
}
```

## 📂 Folder Structure Recommendation

```
src/
├── services/
│   ├── api.ts              # Main API client
│   ├── chatWebSocket.ts    # WebSocket management
│   └── chayenity.ts        # Helper functions
├── hooks/
│   ├── useAuth.ts          # Authentication hook
│   ├── useGigs.ts          # Gigs management hook
│   ├── useChat.ts          # Chat functionality hook
│   └── useUpload.ts        # File upload hook
├── components/
│   ├── LoginForm.tsx       # Login component
│   ├── GigList.tsx         # Gig listing component
│   ├── ChatRoom.tsx        # Chat interface
│   └── FileUpload.tsx      # File upload component
├── types/
│   └── api.ts              # Type definitions
└── utils/
    ├── constants.ts        # API constants
    └── helpers.ts          # Utility functions
```

## 🛠️ Environment Configuration

```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  FILE_UPLOAD_MAX_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
};

// .env.development
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws

// .env.production
REACT_APP_API_URL=https://api.chayenity.com/api
REACT_APP_WS_URL=wss://api.chayenity.com/ws
```

---

**Frontend Integration Guide v1.0** | Last Updated: October 1, 2025