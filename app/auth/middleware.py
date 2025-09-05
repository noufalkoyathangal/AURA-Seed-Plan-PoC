from fastapi import Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Simple authentication middleware for demo purposes
    In production, implement proper JWT validation and role-based access
    """
    
    async def dispatch(self, request: Request, call_next):
        # For demo - allow all requests without authentication
        # Skip auth for health check and docs endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # For API endpoints, you could add authentication here
        # For now, just pass through all requests
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error in AuthMiddleware: {str(e)}")
            # Return the response anyway to avoid blocking the application
            response = await call_next(request)
            return response
