# Gemini Backend Clone

A FastAPI-based backend system that replicates Gemini's functionality with user authentication, chatroom management, AI integration, and subscription handling.

## Features

- **OTP-based Authentication**: Mobile number registration with OTP verification
- **JWT Token Management**: Secure authentication using JWT tokens
- **Chatroom Management**: Create and manage multiple chatrooms per user
- **AI Integration**: Google Gemini API integration for AI responses
- **Async Processing**: Celery with Redis for handling AI API calls
- **Subscription Management**: Stripe integration for Basic/Pro tiers
- **Rate Limiting**: Daily message limits for Basic tier users
- **Caching**: Redis caching for improved performance
- **Webhook Support**: Stripe webhook handling for subscription events

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Queue**: Celery with Redis broker
- **Cache**: Redis
- **Authentication**: JWT with OTP verification
- **Payments**: Stripe (sandbox mode)
- **AI**: Google Gemini API
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gemini-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **run locally**
   ```bash
   # Start PostgreSQL and Redis
   # Run migrations
   alembic upgrade head
   
   # Start the API server
   uvicorn app.main:app --reload
   
   # Start Celery worker
   celery -A app.tasks.gemini_tasks worker --loglevel=info --pool=threads
   ```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/gemini_db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
GEMINI_API_KEY=your_gemini_api_key
ENVIRONMENT=development
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/send-otp` - Send OTP to mobile number
- `POST /auth/verify-otp` - Verify OTP and get JWT token
- `POST /auth/forgot-password` - Send password reset OTP
- `POST /auth/change-password` - Change password (authenticated)

### User Management
- `GET /user/me` - Get current user details

### Chatroom Management
- `POST /chatroom` - Create new chatroom
- `GET /chatroom` - List all chatrooms (cached)
- `GET /chatroom/{id}` - Get chatroom details
- `POST /chatroom/{id}/message` - Send message and get AI response

### Subscription
- `POST /subscribe/pro` - Start Pro subscription
- `GET /subscription/status` - Check subscription status
- `POST /webhook/stripe` - Handle Stripe webhooks

## Architecture Overview

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    mobile_number VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR,
    subscription_tier VARCHAR DEFAULT 'basic',
    daily_message_count INTEGER DEFAULT 0,
    last_message_date TIMESTAMP,
    stripe_customer_id VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- OTPs table
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    mobile_number VARCHAR NOT NULL,
    otp_code VARCHAR NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id)
);

-- Chatrooms table
CREATE TABLE chatrooms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chatroom_id INTEGER REFERENCES chatrooms(id),
    user_message TEXT NOT NULL,
    gemini_response TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Queue System

The application uses Celery with Redis for asynchronous processing:

- **Message Processing**: Gemini API calls are processed asynchronously
- **Task Queue**: Redis serves as both broker and result backend
- **Worker Management**: Celery workers handle AI API integration

### Caching Strategy

Redis caching is implemented for:
- **Chatroom Lists**: 5-minute TTL for `GET /chatroom` endpoint
- **User-specific Cache**: Separate cache keys per user
- **Cache Invalidation**: Automatic invalidation on chatroom creation

### Rate Limiting

- **Basic Tier**: 5 messages per day
- **Pro Tier**: Unlimited messages
- **Daily Reset**: Message counts reset at midnight
- **Middleware**: Rate limiting enforced at API level

## Testing

### Using Postman

1. Import the provided `postman_collection.json`
2. Set the base URL variable to your deployment URL
3. Test the authentication flow:
   - Sign up a new user
   - Send OTP
   - Verify OTP (JWT token will be auto-saved)
   - Access protected endpoints

### Manual Testing Flow

1. **User Registration**
   ```bash
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "1234567890", "password": "password123"}'
   ```

2. **OTP Verification**
   ```bash
   curl -X POST http://localhost:8000/auth/send-otp \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "1234567890"}'
   ```

3. **Get JWT Token**
   ```bash
   curl -X POST http://localhost:8000/auth/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "1234567890", "otp_code": "123456"}'
   ```

4. **Create Chatroom**
   ```bash
   curl -X POST http://localhost:8000/chatroom \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"name": "My First Chat"}'
   ```

5. **Send Message**
   ```bash
   curl -X POST http://localhost:8000/chatroom/1/message \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"user_message": "Hello, how are you?"}'
   ```

## Deployment

### Cloud Deployment

The application is designed to be deployed on:
- **Render**: Use the provided `render.yaml`
- **Railway**: Connect GitHub repository
- **Fly.io**: Use `fly.toml` configuration
- **AWS EC2**: Use Docker or direct deployment

### Environment Setup for Production

1. **Database**: Use managed PostgreSQL service
2. **Redis**: Use managed Redis service
3. **Environment Variables**: Set all required variables
4. **SSL**: Ensure HTTPS in production
5. **Monitoring**: Set up logging and monitoring

## Design Decisions

### Authentication Flow
- **OTP-based**: Chosen for security and user convenience
- **JWT Tokens**: Stateless authentication for scalability
- **Mobile-first**: Primary identifier is mobile number

### Message Processing
- **Async Processing**: Prevents API timeouts for AI responses
- **Celery Integration**: Reliable task queue for background processing
- **Redis Backend**: Fast result storage and retrieval

### Caching Implementation
- **Strategic Caching**: Only cache frequently accessed, slowly changing data
- **TTL Management**: 5-minute TTL for optimal performance/freshness balance
- **Cache Invalidation**: Automatic invalidation on data changes

### Rate Limiting
- **Tier-based**: Different limits for Basic/Pro users
- **Daily Reset**: Clean slate each day for Basic users
- **Middleware Enforcement**: Centralized rate limiting logic

## Monitoring and Logging

### Health Checks
- `GET /health` - Basic health check endpoint
- Database connectivity check
- Redis connectivity check

### Logging
- Structured logging with timestamps
- Request/response logging
- Error tracking and reporting
- Performance monitoring

## Security Considerations

- **Password Hashing**: bcrypt for secure password storage
- **JWT Security**: Proper token expiration and validation
- **Input Validation**: Pydantic models for request validation
- **CORS Configuration**: Proper CORS setup for frontend integration
- **Environment Variables**: Sensitive data in environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
- Open an issue on GitHub

---

**Note**: This is a demonstration project for technical assessment. All API keys and sensitive information should be properly secured in production environments.