# from typing import List

# from crud import crud_plan
# from dependencies import get_db
# from fastapi import APIRouter, Depends, HTTPException
# from schemas.schema import DayPlan, DayPlanCreate
# from sqlalchemy.orm import Session

# router = APIRouter()


# @router.post("/", response_model=DayPlan)
# def create_plan(plan: DayPlanCreate, db: Session = Depends(get_db)):
#     return crud_plan.create_plan(db, plan)


# @router.get("/", response_model=List[DayPlan])
# def read_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return crud_plan.get_plans(db, skip=skip, limit=limit)


# @router.get("/{plan_id}", response_model=DayPlan)
# def read_plan(plan_id: int, db: Session = Depends(get_db)):
#     plan = crud_plan.get_plan(db, plan_id)
#     if plan is None:
#         raise HTTPException(status_code=404, detail="Plan not found")
#     return plan


# @router.delete("/{plan_id}")
# def delete_plan(plan_id: int, db: Session = Depends(get_db)):
#     success = crud_plan.delete_plan(db, plan_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Plan not found")
#     return {"detail": "Plan deleted"}
