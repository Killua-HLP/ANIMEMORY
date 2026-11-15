from app.core.security import create_access_token
import jwt
from app.config import settings

token = create_access_token(user_id=1)

print("Generated token:", token)

payload = jwt.decode(
    token,
    settings.JWT_SECRET_KEY,
    algorithms=[settings.JWT_ALGORITHM]
)

print("Decoded payload:", payload)