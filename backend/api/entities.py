from fastapi import APIRouter, HTTPException
import repositories.entities as repo
from models.responses import APIResponse

router = APIRouter()

@router.get("/{type}")
async def get_entities(type:str):
    result = await repo.get_entities(type)
    return APIResponse(message=f"Get {type} success!", data=result)

@router.post("/{type}/{value}")
async def post_entity(type:str, value:str):
    await repo.post_entity(type, value)
    return APIResponse(message= f"Post {value}: Completed")


@router.get("/{type}/{value}")
async def get_entity(type:str, value):
    result = await repo.get_entity(type, value)
    return APIResponse(message=f"Post {value}: Completed", data=result)