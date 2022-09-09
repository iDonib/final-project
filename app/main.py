import datetime
import operator
import hashlib
from fastapi.staticfiles import StaticFiles
import json
import numpy as np
from fastapi import FastAPI
import requests
from urllib.parse import urlparse
from typing import List
from app.voter import voter_route
from app.checker import write_voted_to_file
from app.models import Voter, Candidate
from app.candidate import candidate_route
from app import models
from fastapi import APIRouter, UploadFile, File, Depends
from app.database import Base, engine
import cv2 as cv
import face_recognition
from app.database import get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="images"), name="static")
router = APIRouter()
app.include_router(voter_route.router)
app.include_router(candidate_route.router)

Base.metadata.create_all(bind=engine)


voted = []

class Blockchain:

    def __init__(self, ):
        self.chain = []
        self.transactions = []
        self.unconfirmed_transactions = []
        self.create_block(proof=1, previous_hash='0', transactions=[])
        self.nodes = set()

    def create_block(self, proof, previous_hash, transactions):
        block = {'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash,
                'transactions': transactions}
        self.transactions = []
        self.chain.append(block)
        return block


    def get_previous_block(self):
        return self.chain[-1]


    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof


    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()


    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True


    def add_transcation(self, sender, receiver):
        self.unconfirmed_transactions.append({
            'sender' : sender,
            'receiver': receiver,
            'amount': 1
            })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1


    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False



blockchain = Blockchain()


@app.get("/mine_block")
def mine_block():
    for i in blockchain.unconfirmed_transactions:
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)
        blockchain.create_block(proof, previous_hash, transactions=i)
    blockchain.unconfirmed_transactions = []
    return {'message': 'Block mined succesfully', 'data': blockchain.chain}


@app.post("/cast_vote")
def add_transcation(receiver_id: str,
        current_image: UploadFile = File(...),
        qr_code: UploadFile = File(...),
        db: Session = Depends(get_db)):
    # check receiver
    data_receiver = db.query(Candidate).filter(Candidate.candidate_id == receiver_id).first()
    if not data_receiver:
        return {"success": False, "message": "Candidate not available"}
    file_bytes = np.fromfile(qr_code.file, np.uint8)
    file = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
    det = cv.QRCodeDetector()
    sender, _, _ = det.detectAndDecode(file)
    a = write_voted_to_file(sender)
    if a is False :
        return {"success": False, "message": "Already Voted"}
    check_validation = db.query(models.Voter).filter(Voter.secret_key == sender).first()
    if check_validation:
        image_location = "./images/" + str(check_validation.picture)
        known_image = face_recognition.load_image_file(image_location)
        unknown_image = face_recognition.load_image_file(current_image.file)
        known_encoding = face_recognition.face_encodings(known_image)[0]
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces([known_encoding], unknown_encoding)
        if results:
            index = blockchain.add_transcation(sender, receiver_id)
            return {'message': f'This transactions will be added to Block {index}'}
    return {'message': 'Invalid accounts'}


@app.post("/connect_node")
def connect_node(nodes_address: List[str]):
    for node in nodes_address:
        blockchain.add_node(node)
    return {'message': "All the nodes are now connected", 'total_nodes': list(blockchain.nodes)}


@app.get('/get_chain')
def get_chain():
    return {'length': len(blockchain.chain), 'chain': blockchain.chain}


@app.get('/is_valid')
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return {'message': 'The blockchain is valid'}
    return {'message': 'The blockchain is not valid'}


@app.get("/replace_chain")
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        return {'message': 'Chain was replaced by longest one', 'new_chain': blockchain.chain}
    return {'message': 'All good. Chain is the largest one', 'new_chain': blockchain.chain}


def return_count(my_list):
    _a = {}
    for i in my_list:
        _a[i] = my_list.count(i)
    return _a

@app.get("/get_vote_count")
def get_vote_count():
    data = {}
    trans_list = []
    network = blockchain.nodes
    for node in network:
        response = requests.get(f'http://{node}/get_chain')
        print(response.status_code)
        if response.status_code == 200:
            length = response.json()['length']
            data[node] = length
    longest_node =  max(data.items(), key=operator.itemgetter(1))[0]
    response = requests.get(f"http://{longest_node}/get_chain")
    chains = response.json()['chain']
    for i in chains:
        trans_list.append(i['transactions'])
    counts = []
    for _i in trans_list:
        if _i:
            counts.append(_i['receiver'])
    return return_count(counts)
