from fastapi import APIRouter, UploadFile, File, Depends
import hashlib
import io
from PIL import Image
import datetime
from app.database import get_db
from app.models import Candidate
from sqlalchemy.orm import Session

# blockchain = architecture.Blockchain()


router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.post("/registration")
async def voter_registration(
        first_name: str,
        last_name: str,
        age: str,
        location: str,
        citizenship_number: str,
        picture:  UploadFile = File(...),
        db: Session = Depends(get_db)
        ):
    if int(age) < 18:
        return {"message": "Age must be greater than 18"}
    picture_file = picture.filename
    picture_extension = picture_file.split('.')[1]
    file_name = first_name + datetime.datetime.now().strftime("%y%m%d_%H%M%S%f")
    pictures = await picture.read()
    picture_image = Image.open(io.BytesIO(pictures))
    picture_image.save('./images/' + file_name + '_picture.' + str(picture_extension))
    new_candidate = Candidate(first_name = first_name,
            last_name = last_name,
            age = age,
            location = location,
            picture = file_name + '_picture.' + str(picture_extension),
            citizenship_number = citizenship_number
            )
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return new_candidate

@router.get('/read/{id}')
def get_candidate_by_id(id: int, db: Session = Depends(get_db)):
    data = db.query(Candidate).filter(Candidate.candidate_id == id).first()
    return data


@router.get('/reads')
def get_all_candidate(db: Session = Depends(get_db)):
    data = db.query(Candidate).filter().all()
    return {"data": data}
