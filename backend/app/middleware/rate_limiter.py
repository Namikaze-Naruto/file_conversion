from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from app.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app, rate_limit: int = None):
        super().__init__(app)
        self.rate_limit = rate_limit or settings.rate_limit_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get current timestamp
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.rate_limit} requests per minute."
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response
