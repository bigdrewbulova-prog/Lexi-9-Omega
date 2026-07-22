from fastapi import APIRouter, HTTPException
from app.schemas import LabCreateRequest, LabResponse
from app.services.lab_runner import create_lab, list_labs, get_lab
from app.labs.ncmi.simulator import run_ncmi_experiment

router = APIRouter(prefix="/labs", tags=["labs"])

@router.post("", response_model=LabResponse)
def create_lab_endpoint(request: LabCreateRequest) -> LabResponse:
    lab = create_lab(request.name, request.description, request.parameters)
    if request.parameters.get("ncmi", False):
        result = run_ncmi_experiment(**request.parameters.get("ncmi", {}))
        lab.result_location = "data/ncmi_experiment.json"
        lab.status = "completed"
        lab.logs = ["NCMI experiment completed"]
        lab = create_lab(lab.name, lab.description, lab.parameters)
    return LabResponse(
        id=lab.id,
        name=lab.name,
        description=lab.description,
        status=lab.status,
        created_at=lab.created_at,
        updated_at=lab.updated_at,
        parameters=lab.parameters,
        logs=lab.logs,
        result_location=lab.result_location,
    )

@router.get("", response_model=list[LabResponse])
def list_labs_endpoint() -> list[LabResponse]:
    labs = list_labs()
    return [LabResponse(
        id=lab.id,
        name=lab.name,
        description=lab.description,
        status=lab.status,
        created_at=lab.created_at,
        updated_at=lab.updated_at,
        parameters=lab.parameters,
        logs=lab.logs,
        result_location=lab.result_location,
    ) for lab in labs]

@router.get("/{experiment_id}", response_model=LabResponse)
def get_lab_endpoint(experiment_id: str) -> LabResponse:
    lab = get_lab(experiment_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return LabResponse(
        id=lab.id,
        name=lab.name,
        description=lab.description,
        status=lab.status,
        created_at=lab.created_at,
        updated_at=lab.updated_at,
        parameters=lab.parameters,
        logs=lab.logs,
        result_location=lab.result_location,
    )
