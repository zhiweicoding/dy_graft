import json
import uuid

from fastapi import APIRouter, Request, Depends, HTTPException
from app.entity.base_response import BaseResponse
from app.db.postgres_db import RecordAction, RecordActionSchema
from app.dependencies import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/query/list", response_model=BaseResponse)
async def query_list(db: Session = Depends(get_db)):
    query_array = db.query(RecordAction).filter(RecordAction.is_delete is False).all()
    if query_array is None:
        raise HTTPException(status_code=500, detail="data not found")
    return BaseResponse(code=200, message="success",
                        data=[RecordActionSchema.from_orm(item) for item in query_array]).json()


@router.post("/msg/add", response_model=BaseResponse)
async def add_msg(request: Request, db: Session = Depends(get_db)):
    # Parse the incoming JSON data
    data = await request.json()
    # msg_data = MsgSchema(**data)
    new_msg = RecordAction(
        record_id=str(uuid.uuid4()),
        input_url_params='',
        input_args=json.dumps(data),
        type='dy',
        mix_type='0',
        output_body='body',
        visitor_id='anonymous',
        creator='python_service',
        updater='python_service',
        is_delete=False,

    )
    # Add the new message to the database session
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return BaseResponse(code=200, message="success")


@router.put("/msg/update", response_model=BaseResponse)
async def update_msg(request: Request, db: Session = Depends(get_db)):
    # Parse the incoming JSON data
    data = await request.json()
    # Convert the JSON data to MsgSchema
    msg_data = RecordActionSchema(**data)
    # Query the existing message
    existing_msg = db.query(RecordAction).filter(RecordAction.record_id == msg_data.record_id).first()
    if existing_msg is None:
        return BaseResponse(code=404, message="Message not found")

    # Update the existing message's fields
    existing_msg.output_body = msg_data.output_body

    # Commit the changes
    db.commit()
    db.refresh(existing_msg)
    return BaseResponse(code=200, message="success")


@router.delete("/msg/delete/{record_id}", response_model=BaseResponse)
async def delete_msg(record_id: str, db: Session = Depends(get_db)):
    existing_msg: RecordAction = db.query(RecordAction).filter(RecordAction.record_id == record_id).first()
    if existing_msg is None:
        return BaseResponse(code=404, message="Message not found")

    existing_msg.record_id = record_id
    existing_msg.is_delete = False

    # Commit the changes
    db.commit()
    db.refresh(existing_msg)
    return BaseResponse(code=200, message="success")
