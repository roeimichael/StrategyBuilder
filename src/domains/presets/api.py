from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from src.domains.presets.models import CreatePresetRequest, UpdatePresetRequest, PresetResponse, PresetListResponse
from src.domains.presets.repository import PresetRepository
from src.shared.utils.api_logger import log_errors

router = APIRouter(prefix="/presets", tags=["presets"])
preset_repository = PresetRepository()


@router.post("", response_model=PresetResponse, status_code=201)
@log_errors
def create_preset(request: CreatePresetRequest) -> PresetResponse:
    """
    Create a new strategy preset (configuration without a specific ticker).

    - **name**: Unique name for the preset
    - **description**: Optional description
    - **strategy**: Strategy name
    - **parameters**: Strategy parameters
    - **interval**: Data interval (default: 1d)
    - **cash**: Starting cash amount (default: 10000)
    """
    try:
        # Check if name already exists
        existing = preset_repository.get_preset_by_name(request.name)
        if existing:
            raise HTTPException(status_code=400, detail=f"Preset with name '{request.name}' already exists")

        preset_id = preset_repository.create_preset({
            'name': request.name,
            'description': request.description,
            'strategy': request.strategy,
            'parameters': request.parameters,
            'interval': request.interval,
            'cash': request.cash
        })

        preset = preset_repository.get_preset_by_id(preset_id)
        return PresetResponse(**preset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {str(e)}")


@router.get("", response_model=PresetListResponse)
@log_errors
def list_presets(
    strategy: Optional[str] = Query(None, description="Filter by strategy name"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=500),
    offset: int = Query(0, description="Number of results to skip", ge=0)
) -> PresetListResponse:
    """
    List all strategy presets with optional filters.

    - **strategy**: Filter by strategy name (optional)
    - **limit**: Maximum number of results (default: 100, max: 500)
    - **offset**: Number of results to skip for pagination
    """
    try:
        presets = preset_repository.list_presets(strategy=strategy, limit=limit, offset=offset)
        preset_responses = [PresetResponse(**preset) for preset in presets]

        return PresetListResponse(
            success=True,
            count=len(preset_responses),
            presets=preset_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve presets: {str(e)}")


@router.get("/{preset_id}", response_model=PresetResponse)
@log_errors
def get_preset(preset_id: int) -> PresetResponse:
    """
    Get a specific preset by ID.

    - **preset_id**: The ID of the preset
    """
    try:
        preset = preset_repository.get_preset_by_id(preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")

        return PresetResponse(**preset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve preset: {str(e)}")


@router.patch("/{preset_id}", response_model=PresetResponse)
@log_errors
def update_preset(preset_id: int, request: UpdatePresetRequest) -> PresetResponse:
    """
    Update an existing preset.

    - **preset_id**: The ID of the preset to update
    - **request**: Fields to update (all optional)
    """
    try:
        # Check if preset exists
        existing = preset_repository.get_preset_by_id(preset_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")

        # Build updates dict
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.parameters is not None:
            updates['parameters'] = request.parameters
        if request.interval is not None:
            updates['interval'] = request.interval
        if request.cash is not None:
            updates['cash'] = request.cash

        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")

        success = preset_repository.update_preset(preset_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preset")

        preset = preset_repository.get_preset_by_id(preset_id)
        return PresetResponse(**preset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preset: {str(e)}")


@router.delete("/{preset_id}", status_code=204)
@log_errors
def delete_preset(preset_id: int):
    """
    Delete a preset.

    - **preset_id**: The ID of the preset to delete
    """
    try:
        success = preset_repository.delete_preset(preset_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Preset with ID {preset_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete preset: {str(e)}")
