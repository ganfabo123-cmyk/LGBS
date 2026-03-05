from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter()

# 内存存储，实际项目中应该使用数据库
projects: Dict[str, Dict] = {}

class AppDefinition(BaseModel):
    app_name: str
    app_description: str
    initial_inputs: List[str]
    final_outputs: List[str]

class NodeDefinition(BaseModel):
    name: str
    description: str
    type: str
    inputs: List[str]
    outputs: List[str]
    prompt_template: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None

class ConnectionDefinition(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    condition: Optional[str] = None
    
    class Config:
        populate_by_name = True

class ModuleDefinition(BaseModel):
    module_name: str
    module_description: str
    module_inputs: List[str] = []
    module_outputs: List[str] = []
    nodes: List[NodeDefinition]
    connections: List[ConnectionDefinition] = []

class StateDefinition(BaseModel):
    variables: List[Dict[str, Any]]

class MappingDefinition(BaseModel):
    mappings: List[Dict[str, Any]]

class ProjectCreate(BaseModel):
    app_definition: AppDefinition
    modules: List[ModuleDefinition]
    state_definition: StateDefinition
    mapping_definition: MappingDefinition

class ProjectUpdate(BaseModel):
    app_definition: Optional[AppDefinition] = None
    modules: Optional[List[ModuleDefinition]] = None
    state_definition: Optional[StateDefinition] = None
    mapping_definition: Optional[MappingDefinition] = None

@router.post("/create")
async def create_project(project: ProjectCreate) -> Dict[str, Any]:
    project_id = f"project_{len(projects) + 1}"
    projects[project_id] = project.model_dump()
    return {"project_id": project_id, "project": projects[project_id]}

@router.get("/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id]

@router.put("/{project_id}")
async def update_project(project_id: str, project: ProjectUpdate) -> Dict[str, Any]:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.model_dump(exclude_unset=True)
    projects[project_id].update(update_data)
    return projects[project_id]

@router.delete("/{project_id}")
async def delete_project(project_id: str) -> Dict[str, str]:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects[project_id]
    return {"message": "Project deleted successfully"}

@router.post("/module/export/{project_id}/{module_name}")
async def export_module(project_id: str, module_name: str) -> Dict[str, Any]:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    for module in project.get("modules", []):
        if module.get("module_name") == module_name:
            return module
    
    raise HTTPException(status_code=404, detail="Module not found")

@router.post("/module/import/{project_id}")
async def import_module(project_id: str, module: ModuleDefinition) -> Dict[str, Any]:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    modules = project.get("modules", [])
    
    # 检查模块是否已存在
    existing_module_index = next(
        (i for i, m in enumerate(modules) if m.get("module_name") == module.module_name),
        None
    )
    
    if existing_module_index is not None:
        # 更新现有模块
        modules[existing_module_index] = module.model_dump()
    else:
        # 添加新模块
        modules.append(module.model_dump())
    
    project["modules"] = modules
    return project
