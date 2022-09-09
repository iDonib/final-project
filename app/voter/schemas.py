from pydantic import BaseModel
from typing import  List


class CastVote(BaseModel):
    public_key: str
    facial_points: List[float] = [] 
    candidate_key: str

class VoterRegistration(BaseModel):
    first_name: str
    last_name: str
    middle_name: str | None = None
    age: int
    location: str
    face_encoded_list: List[float]
