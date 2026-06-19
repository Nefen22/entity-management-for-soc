from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("/{type}")
async def get_entities(type:str):
    result = await services.get_entities(type)
    return APIResponse(message=f"Get {type} success!", data=result)

@router.post("/{type}/{value}")
async def post_entity(type:str, value):
    await services.post_entity(type, value)

@router.get("/{type}/{value}")
async def get_entity(type:str, value):
    result = await services.get_entity(type, value)
    return APIResponse(message=f"Get {value}: Completed", data=result)