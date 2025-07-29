# from typing import List

# from crud import crud_time
# from dependencies import get_db
# from fastapi import APIRouter, Depends, HTTPException
# from schemas.schema import Time, TimeCreate
# from sqlalchemy.orm import Session

# router = APIRouter()


# @router.post("/", response_model=Time)
# def create_time(time: TimeCreate, db: Session = Depends(get_db)):
#     return crud_time.create_time(db, time)


# @router.get("/", response_model=List[Time])
# def read_times(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return crud_time.get_times(db, skip=skip, limit=limit)


# @router.get("/{time_id}", response_model=Time)
# def read_plan(time_id: int, db: Session = Depends(get_db)):
#     time = crud_time.get_time(db, time_id)
#     if time is None:
#         raise HTTPException(status_code=404, detail="Time not found")
#     return time


# @router.delete("/{time_id}")
# def delete_time(time_id: int, db: Session = Depends(get_db)):
#     success = crud_time.delete_time(db, time_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Time not found")
#     return {"detail": "Time deleted"}
