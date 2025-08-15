from functools import wraps
from domain.exceptions import BadRequestError, NotFoundError
from fastapi import HTTPException

def handle_service_result(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):  # Make it async
        try:
            return await func(*args, **kwargs)  # Await the async function
        except BadRequestError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except NotFoundError as ne:
            raise HTTPException(status_code=404, detail=str(ne))
        except PermissionError as pe:
            raise HTTPException(status_code=403, detail=str(pe))
        except Exception as ie:
            raise HTTPException(status_code=500, detail=str(ie))  # Avoid exposing raw errors in prod

    return wrapper