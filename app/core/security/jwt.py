from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request, HTTPException, status
from app.core.config.settings import settings
from app.core.commons.exceptions import UnauthorizedException
from app.model.usuario_model import Usuario
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTManager:
    """Gerenciador de tokens JWT"""
    
    @staticmethod
    def extract_token(request: Request) -> str:
        """
        Extrai o token JWT do header Authorization.
        Formato esperado: 'Bearer <token>'
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise UnauthorizedException("Token não fornecido ou formato inválido")
        return auth_header.split(" ")[1]
    
    @staticmethod
    def create_access_token(usuario: Usuario) -> str:
        """Cria um token JWT de acesso"""
        try:
            expire = datetime.utcnow() + settings.access_token_expires
            to_encode = {
                "exp": expire,
                "sub": str(usuario.id),
                "matricula": usuario.matricula,
                "email": usuario.email,
                "nome": usuario.nome,
                "iat": datetime.utcnow(),
                "type": "access"
            }
            return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
        except Exception as e:
            raise UnauthorizedException(f"Erro ao criar token de acesso: {str(e)}")

    @staticmethod
    def create_refresh_token(usuario: Usuario) -> str:
        """Cria um token JWT de refresh"""
        try:
            expire = datetime.utcnow() + settings.refresh_token_expires
            to_encode = {
                "exp": expire,
                "sub": str(usuario.id),
                "matricula": usuario.matricula,
                "email": usuario.email,
                "nome": usuario.nome,

                "iat": datetime.utcnow(),
                "type": "refresh"
            }
            return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
        except Exception as e:
            raise UnauthorizedException(f"Erro ao criar token de refresh: {str(e)}")

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verifica e decodifica um token JWT"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                raise UnauthorizedException("Token inválido")
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token expirado")
        except jwt.JWTError:
            raise UnauthorizedException("Token inválido")
        except Exception as e:
            raise UnauthorizedException(f"Erro na verificação do token: {str(e)}")

    @staticmethod
    def verify_refresh_token(token: str) -> str:
        """Verifica um token de refresh"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Token de refresh inválido")
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token de refresh expirado")
        except jwt.JWTError:
            raise UnauthorizedException("Token de refresh inválido")
        except Exception as e:
            raise UnauthorizedException(f"Erro na verificação do token de refresh: {str(e)}")

    @staticmethod
    def create_password_reset_token(subject: Any) -> str:
        """Cria um token para reset de senha"""
        try:
            expire = datetime.utcnow() + timedelta(hours=24)
            to_encode = {
                "exp": expire,
                "sub": str(subject),
                "iat": datetime.utcnow(),
                "type": "password_reset"
            }
            return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
        except Exception as e:
            raise UnauthorizedException(f"Erro ao criar token de reset de senha: {str(e)}")

    @staticmethod
    def verify_password_reset_token(token: str) -> str:
        """Verifica um token de reset de senha"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
            if payload.get("type") != "password_reset":
                raise UnauthorizedException("Token inválido")
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token expirado")
        except jwt.JWTError:
            raise UnauthorizedException("Token inválido")
        except Exception as e:
            raise UnauthorizedException(f"Erro ao verificar token de reset de senha: {str(e)}")

    @staticmethod
    def get_token_payload(request: Request) -> Dict[str, Any]:
        """
        Extrai e valida o token JWT do request, retornando o payload.
        Útil para endpoints que precisam apenas validar o token sem precisar do usuário.
        """
        token = JWTManager.extract_token(request)
        return JWTManager.verify_token(token)