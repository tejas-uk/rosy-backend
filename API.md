# Lily Chat API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (development)  
**Description:** Pediatric nurse AI chat API for supporting expectant mothers and caregivers

## Table of Contents

- [Authentication](#authentication)
- [User Management](#user-management)
- [Chat Management](#chat-management)
- [Error Handling](#error-handling)
- [React/TypeScript Client](#reacttypescript-client)
- [Data Models](#data-models)

## Authentication

Currently, the API uses simple username/password authentication. User credentials are hashed using SHA256 and stored in the database.

## User Management

### Register New User

Create a new user account.

**Endpoint:** `POST /users/register`

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string" // optional
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "message": "User created successfully"
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mom_sarah",
    "password": "secure123",
    "email": "sarah@email.com"
  }'
```

**Example - React/TypeScript:**
```typescript
interface UserRegister {
  username: string;
  password: string;
  email?: string;
}

interface UserResponse {
  user_id: string;
  username: string;
  message: string;
}

const registerUser = async (userData: UserRegister): Promise<UserResponse> => {
  const response = await fetch('http://localhost:8000/users/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    throw new Error(`Registration failed: ${response.statusText}`);
  }

  return response.json();
};

// Usage
const handleRegister = async () => {
  try {
    const result = await registerUser({
      username: 'mom_sarah',
      password: 'secure123',
      email: 'sarah@email.com'
    });
    console.log('User registered:', result.user_id);
  } catch (error) {
    console.error('Registration error:', error);
  }
};
```

### Login User

Authenticate an existing user.

**Endpoint:** `POST /users/login`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "message": "Login successful"
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mom_sarah",
    "password": "secure123"
  }'
```

**Example - React/TypeScript:**
```typescript
interface UserLogin {
  username: string;
  password: string;
}

const loginUser = async (credentials: UserLogin): Promise<UserResponse> => {
  const response = await fetch('http://localhost:8000/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`);
  }

  return response.json();
};

// Usage with React state
const [user, setUser] = useState<UserResponse | null>(null);

const handleLogin = async () => {
  try {
    const result = await loginUser({
      username: 'mom_sarah',
      password: 'secure123'
    });
    setUser(result);
    localStorage.setItem('user_id', result.user_id);
  } catch (error) {
    console.error('Login error:', error);
  }
};
```

### Get User's Chat Threads

Retrieve all chat threads for a specific user.

**Endpoint:** `GET /users/{user_id}/chats`

**Response:**
```json
{
  "user_id": "uuid",
  "threads": [
    {
      "thread_id": "uuid",
      "created_at": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

**Example - curl:**
```bash
curl -X GET "http://localhost:8000/users/d1714a72-be29-4b56-893d-0bb9770c75e1/chats"
```

**Example - React/TypeScript:**
```typescript
interface ChatThread {
  thread_id: string;
  created_at: string;
}

interface UserChatsResponse {
  user_id: string;
  threads: ChatThread[];
}

const getUserChats = async (userId: string): Promise<UserChatsResponse> => {
  const response = await fetch(`http://localhost:8000/users/${userId}/chats`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch chats: ${response.statusText}`);
  }

  return response.json();
};

// Usage in React component
const ChatList: React.FC<{ userId: string }> = ({ userId }) => {
  const [chats, setChats] = useState<ChatThread[]>([]);

  useEffect(() => {
    const loadChats = async () => {
      try {
        const result = await getUserChats(userId);
        setChats(result.threads);
      } catch (error) {
        console.error('Error loading chats:', error);
      }
    };

    loadChats();
  }, [userId]);

  return (
    <div>
      {chats.map(chat => (
        <div key={chat.thread_id}>
          Chat: {chat.thread_id} - {new Date(chat.created_at).toLocaleDateString()}
        </div>
      ))}
    </div>
  );
};
```

## Chat Management

### Create New Chat Thread

Create a new chat conversation for a user.

**Endpoint:** `POST /chat/new`

**Request Body:**
```json
{
  "user_id": "uuid"
}
```

**Response:**
```json
{
  "thread_id": "uuid",
  "user_id": "uuid"
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/chat/new" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "d1714a72-be29-4b56-893d-0bb9770c75e1"
  }'
```

**Example - React/TypeScript:**
```typescript
interface ChatCreate {
  user_id: string;
}

interface ChatResponse {
  thread_id: string;
  user_id: string;
}

const createChat = async (userId: string): Promise<ChatResponse> => {
  const response = await fetch('http://localhost:8000/chat/new', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create chat: ${response.statusText}`);
  }

  return response.json();
};

// Usage in React component
const NewChatButton: React.FC<{ userId: string; onChatCreated: (chat: ChatResponse) => void }> = 
  ({ userId, onChatCreated }) => {
  
  const handleCreateChat = async () => {
    try {
      const newChat = await createChat(userId);
      onChatCreated(newChat);
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  };

  return (
    <button onClick={handleCreateChat}>
      Start New Conversation with Lily
    </button>
  );
};
```

### Load Chat Conversation

Retrieve the complete conversation history for a specific chat thread.

**Endpoint:** `GET /chat/{user_id}/{thread_id}`

**Response:**
```json
{
  "thread_id": "uuid",
  "user_id": "uuid",
  "messages": [
    {
      "type": "human",
      "content": "Hello, I need help with my baby!",
      "timestamp": null
    },
    {
      "type": "ai",
      "content": "Hi there! I'm here to help you and your little one...",
      "timestamp": null
    }
  ]
}
```

**Example - curl:**
```bash
curl -X GET "http://localhost:8000/chat/d1714a72-be29-4b56-893d-0bb9770c75e1/1f0622b9-8ceb-48e4-b0c2-427afa4d97a2"
```

**Example - React/TypeScript:**
```typescript
interface MessageResponse {
  type: 'human' | 'ai';
  content: string;
  timestamp: string | null;
}

interface ChatHistory {
  thread_id: string;
  user_id: string;
  messages: MessageResponse[];
}

const getChatHistory = async (userId: string, threadId: string): Promise<ChatHistory> => {
  const response = await fetch(`http://localhost:8000/chat/${userId}/${threadId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to load chat: ${response.statusText}`);
  }

  return response.json();
};

// Chat component
const ChatWindow: React.FC<{ userId: string; threadId: string }> = ({ userId, threadId }) => {
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadChat = async () => {
      try {
        setLoading(true);
        const history = await getChatHistory(userId, threadId);
        setMessages(history.messages);
      } catch (error) {
        console.error('Error loading chat:', error);
      } finally {
        setLoading(false);
      }
    };

    loadChat();
  }, [userId, threadId]);

  if (loading) return <div>Loading conversation...</div>;

  return (
    <div className="chat-window">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.type}`}>
          <strong>{message.type === 'human' ? 'You' : 'Lily'}:</strong>
          <p>{message.content}</p>
        </div>
      ))}
    </div>
  );
};
```

### Send Message

Send a message to a chat thread and receive Lily's response.

**Endpoint:** `POST /chat/{user_id}/{thread_id}/message`

**Request Body:**
```json
{
  "message": "string"
}
```

**Response:**
```json
{
  "type": "ai",
  "content": "Lily's response message",
  "timestamp": null
}
```

**Example - curl:**
```bash
curl -X POST "http://localhost:8000/chat/d1714a72-be29-4b56-893d-0bb9770c75e1/1f0622b9-8ceb-48e4-b0c2-427afa4d97a2/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "My baby has been crying a lot. What should I do?"}'
```

**Example - React/TypeScript:**
```typescript
interface MessageSend {
  message: string;
}

const sendMessage = async (
  userId: string, 
  threadId: string, 
  message: string
): Promise<MessageResponse> => {
  const response = await fetch(
    `http://localhost:8000/chat/${userId}/${threadId}/message`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
};

// Chat input component
const ChatInput: React.FC<{
  userId: string;
  threadId: string;
  onMessageSent: (userMessage: string, aiResponse: MessageResponse) => void;
}> = ({ userId, threadId, onMessageSent }) => {
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || sending) return;

    try {
      setSending(true);
      const userMessage = message;
      setMessage(''); // Clear input immediately

      const aiResponse = await sendMessage(userId, threadId, userMessage);
      onMessageSent(userMessage, aiResponse);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessage(message); // Restore message on error
    } finally {
      setSending(false);
    }
  };

  return (
    <form onSubmit={handleSend} className="chat-input">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask Lily about your baby..."
        disabled={sending}
      />
      <button type="submit" disabled={sending || !message.trim()}>
        {sending ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};
```

### Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Lily Chat API"
}
```

**Example - curl:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Example - React/TypeScript:**
```typescript
const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

// Usage in app initialization
useEffect(() => {
  const verifyConnection = async () => {
    const isHealthy = await checkHealth();
    if (!isHealthy) {
      console.error('API is not available');
    }
  };

  verifyConnection();
}, []);
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Username already exists"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid username or password"
}
```

**404 Not Found:**
```json
{
  "detail": "Chat thread not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Database error: [specific error message]"
}
```

### Error Handling in React/TypeScript

```typescript
class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const handleApiResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, errorData.detail || response.statusText);
  }
  return response.json();
};

// Usage with error handling
const safeApiCall = async <T>(apiCall: () => Promise<T>): Promise<T | null> => {
  try {
    return await apiCall();
  } catch (error) {
    if (error instanceof ApiError) {
      switch (error.status) {
        case 401:
          // Handle authentication error
          console.error('Authentication failed:', error.message);
          // Redirect to login
          break;
        case 404:
          console.error('Resource not found:', error.message);
          break;
        case 500:
          console.error('Server error:', error.message);
          break;
        default:
          console.error('API error:', error.message);
      }
    } else {
      console.error('Network error:', error);
    }
    return null;
  }
};
```

## React/TypeScript Client

### Complete Chat Application Example

```typescript
import React, { useState, useEffect } from 'react';

// Types
interface User {
  user_id: string;
  username: string;
}

interface Chat {
  thread_id: string;
  user_id: string;
}

interface Message {
  type: 'human' | 'ai';
  content: string;
}

// Main App Component
const LilyChatApp: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUserId = localStorage.getItem('user_id');
    const savedUsername = localStorage.getItem('username');
    
    if (savedUserId && savedUsername) {
      setUser({ user_id: savedUserId, username: savedUsername });
    }
  }, []);

  const handleLogin = async (username: string, password: string) => {
    try {
      const result = await loginUser({ username, password });
      setUser(result);
      localStorage.setItem('user_id', result.user_id);
      localStorage.setItem('username', result.username);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleCreateChat = async () => {
    if (!user) return;
    
    try {
      const newChat = await createChat(user.user_id);
      setCurrentChat(newChat);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create chat:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!user || !currentChat) return;

    try {
      // Add user message immediately
      const userMessage: Message = { type: 'human', content: message };
      setMessages(prev => [...prev, userMessage]);

      // Send to API and get response
      const aiResponse = await sendMessage(user.user_id, currentChat.thread_id, message);
      const aiMessage: Message = { type: 'ai', content: aiResponse.content };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  if (!user) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="lily-chat-app">
      <header>
        <h1>Chat with Lily 🧚‍♂️</h1>
        <p>Welcome, {user.username}!</p>
      </header>

      {!currentChat ? (
        <div className="no-chat">
          <p>Start a conversation with Lily, your pediatric nurse assistant!</p>
          <button onClick={handleCreateChat}>Start New Chat</button>
        </div>
      ) : (
        <div className="chat-container">
          <ChatWindow messages={messages} />
          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      )}
    </div>
  );
};

export default LilyChatApp;
```

## Data Models

### User
```typescript
interface User {
  user_id: string;      // UUID
  username: string;     // Unique username
  email?: string;       // Optional email
}
```

### Chat Thread
```typescript
interface ChatThread {
  thread_id: string;    // UUID
  user_id: string;      // UUID reference to user
  created_at: string;   // ISO datetime string
}
```

### Message
```typescript
interface Message {
  type: 'human' | 'ai'; // Message sender type
  content: string;      // Message content
  timestamp?: string;   // Optional timestamp
}
```

### Configuration Format

When working with the LangGraph agent internally, the configuration format is:

```typescript
{
  "configurable": {
    "thread_id": "uuid",
    "user_id": "uuid"
  }
}
```

This ensures proper conversation persistence and user isolation in the PostgreSQL checkpointer.

## Running the API

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

3. **Initialize database:**
   ```bash
   python utils/init_db.py
   ```

4. **Start the server:**
   ```bash
   python api.py
   ```

The API will be available at `http://localhost:8000` with automatic API documentation at `http://localhost:8000/docs`.