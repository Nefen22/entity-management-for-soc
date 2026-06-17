from fastapi import APIRouter, HTTPException
import repositories.entities as repo
from models.responses import APIResponse

router = APIRouter()

@router.post("/{type}/{value}")
async def post_entities(type:str, value:str):
    await repo.post_entities(type, value)
    return APIResponse(message= f"Post {value}: Completed")


@router.get("/{type}/{value}")
async def get_entities(type:str, value):
    result = await repo.get_entities(type, value)
    return APIResponse(message=f"Post {value}: Completed", data=result)