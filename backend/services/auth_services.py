from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from services import user_services
from fastapi import HTTPException, status, Depends, Security
from database import db
import bcrypt
import os
from fastapi import HTTPException


SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_for_local_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # La duración de validez del token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generar el salt
    salt = bcrypt.gensalt()
    # Hashear la contraseña con el salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def authenticate_user(username, password):
    # Buscar al usuario por correo electrónico
    user = await db.get_collection("users").find_one({"email": username})
    
    if not user:
        # Levanta una excepción si el usuario no se encuentra
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, user['password']):
        # Levanta una excepción si la contraseña no es correcta
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Si la autenticación es exitosa, retorna el documento del usuario
    return user

def format_token(user):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user['email'], expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user['_id']),
        "email": user['email']
    }

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Genera un token de acceso JWT."""
    claims = {"sub": subject}
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    claims.update({"exp": expire})
    token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await user_services.get_user_by_email(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
