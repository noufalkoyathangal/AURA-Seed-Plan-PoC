from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List

security = HTTPBearer(auto_error=False)

def require_permission(permission: str):
    """
    Dependency that checks user permissions
    """
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
        # For demo purposes - replace with real JWT validation
        if not credentials:
            # Return demo user for development
            return {
                "id": "demo_user_123",
                "name": "Demo Planner",
                "email": "demo@intelo.ai",
                "permissions": ["seed:create", "seed:execute", "seed:validate", "seed:approve", "cluster:create", "seed:view"],
                "role": "planner"
            }
        
        # TODO: Implement JWT token validation
        user_data = validate_jwt_token(credentials.credentials)
        
        # Check permissions
        if permission not in user_data.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        
        return user_data
    
    return dependency

def validate_jwt_token(token: str) -> Dict:
    """
    Validate JWT token and return user data
    """
    # TODO: Implement actual JWT validation
    return {
        "id": "user_from_jwt",
        "name": "Authenticated User", 
        "email": "user@retailer.com",
        "permissions": ["seed:create", "seed:execute"],
        "role": "merchant"
    }
