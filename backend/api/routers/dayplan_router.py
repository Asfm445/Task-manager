from api.dependencies import get_current_user, get_dayplan_usecase
from api.schemas.dayplan_schema import DayPlan, DayPlanCreate, Time, TimeCreate
from api.utilities.handle_service_result import handle_service_result
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/dayplan", response_model=DayPlan)
@handle_service_result
def get_dayplan(
    dayplan: DayPlanCreate,
    usecase=Depends(get_dayplan_usecase),
    current_user=Depends(get_current_user),
):
    return usecase.get_dayplan(dayplan.date, current_user)


@router.delete("/dayplan", response_model=DayPlan)
@handle_service_result
def delete_dayplan(
    dayplan: DayPlanCreate,
    usecase=Depends(get_dayplan_usecase),
    current_user=Depends(get_current_user),
):
    return usecase.delete_dayplan(dayplan.date, current_user)


@router.post("/timelog", response_model=Time)
@handle_service_result
def create_timelog(
    time_log: TimeCreate,
    usecase=Depends(get_dayplan_usecase),
    current_user=Depends(get_current_user),
):
    return usecase.create_timelog(time_log, current_user)


@router.delete("/timelog/{time_log_id}", response_model=Time)
@handle_service_result
def delete_timelog(
    time_log_id: int,
    usecase=Depends(get_dayplan_usecase),
    current_user=Depends(get_current_user),
):
    return usecase.delete_timelog(time_log_id, current_user)
