from fastapi import APIRouter
from src.api.endpoints import project, codegen

router = APIRouter()

router.include_router(project.router, prefix="/project", tags=["project"])
router.include_router(codegen.router, prefix="/codegen", tags=["codegen"])
