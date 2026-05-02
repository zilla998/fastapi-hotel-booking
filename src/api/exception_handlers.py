from authx.exceptions import AuthXException, JWTDecodeError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.enums import ErrorCode


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(JWTDecodeError, jwt_decode_exception_handler)
    app.add_exception_handler(AuthXException, authx_exception_handler)


async def jwt_decode_exception_handler(request: Request, exc: JWTDecodeError):
    code = ErrorCode.TOKEN_EXPIRED if "expired" in str(exc).lower() else ErrorCode.UNAUTHORIZED
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": {"code": code}},
    )


async def authx_exception_handler(request: Request, exc: AuthXException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": {"code": ErrorCode.UNAUTHORIZED}},
    )
