from fastapi import APIRouter, UploadFile, File, Depends
import hashlib
import io
from PIL import Image
import datetime
import qrcode
from app.database import get_db
from app.models import Voter
from sqlalchemy.orm import Session

# blockchain = architecture.Blockchain()


router = APIRouter(prefix="/voter", tags=["voters"])

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
    picture_file = picture.filename
    picture_extension = picture_file.split('.')[1]
    user_data = {'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'location': location,
            'picture': 's',
            'citizenship_number': citizenship_number}
    encrypted_data = hashlib.sha512(str(user_data).encode()).hexdigest()
    writeable_data = [encrypted_data]
    file_name = first_name + datetime.datetime.now().strftime("%y%m%d_%H%M%S%f")
    img = qrcode.make(encrypted_data)
    img.save(f'./images/{file_name}_qr.png')
    pictures = await picture.read()
    picture_image = Image.open(io.BytesIO(pictures))
    picture_image.save('./images/' + file_name + '_picture.' + str(picture_extension))
    new_voter = Voter(first_name = first_name,
            last_name = last_name,
            age = age,
            location = location,
            picture = file_name + '_picture.' + str(picture_extension),
            qr_code = file_name + '_qr'+ '.png',
            secret_key = encrypted_data,
            citizenship_number = citizenship_number
            )
    db.add(new_voter)
    db.commit()
    db.refresh(new_voter)
    new_voter.encrypted_data = None
    return {"data" :new_voter}


@router.get("/read/{id}")
def get_voter_by_id(id: int, db: Session = Depends(get_db)):
    data = db.query(Voter).filter(Voter.voter_id == id).first()
    return data


@router.get("/")
def get_all_voter(db: Session = Depends(get_db)):
    # data = db.query(Voter).filter(Voter.voter_id == 1).first()
    data = db.query(Voter).all()
    return data
