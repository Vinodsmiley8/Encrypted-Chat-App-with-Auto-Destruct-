"""FastAPI server for Encrypted Chat with Auto-Destruct

- /register : register user public keys
- /send     : send encrypted message (server stores ciphertext only)
- /receive  : recipient fetches their messages; server deletes them after returning (auto-destruct)
"""
import base64
import time
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI(title='Encrypted Chat Auto-Destruct (Demo)')

# Simple in-memory stores (demo only)
# user_id -> base64 public key
user_public_keys = {}
# recipient_id -> list of message dicts
messages = {}

# message structure:
# {
#   "id": str,
#   "sender": str,
#   "ciphertext_b64": str,
#   "created_at": float,
#   "expire_at": Optional[float]  # unix ts
# }

class RegisterRequest(BaseModel):
    user_id: str
    public_key_b64: str

class SendRequest(BaseModel):
    sender: str
    recipient: str
    ciphertext_b64: str
    ttl_seconds: Optional[int] = None  # optional expiration in seconds

@app.post('/register')
async def register(req: RegisterRequest):
    user_public_keys[req.user_id] = req.public_key_b64
    return {'status':'ok', 'user_id': req.user_id}

@app.get('/public_key/{user_id}')
async def get_public_key(user_id: str):
    pk = user_public_keys.get(user_id)
    if not pk:
        raise HTTPException(status_code=404, detail='Public key not found')
    return {'user_id': user_id, 'public_key_b64': pk}

@app.post('/send')
async def send_message(req: SendRequest):
    if req.recipient not in messages:
        messages[req.recipient] = []
    msg_id = f"msg-{int(time.time()*1000)}-{len(messages[req.recipient])}"
    now = time.time()
    expire = None
    if req.ttl_seconds:
        expire = now + req.ttl_seconds
    messages[req.recipient].append({
        'id': msg_id,
        'sender': req.sender,
        'ciphertext_b64': req.ciphertext_b64,
        'created_at': now,
        'expire_at': expire
    })
    return {'status':'stored','id':msg_id}

@app.get('/receive/{user_id}')
async def receive_messages(user_id: str):
    # Return ciphertexts and delete them immediately (auto-destruct)
    user_msgs = messages.get(user_id, [])
    if not user_msgs:
        return {'messages': []}
    # filter out expired
    now = time.time()
    deliver = []
    remaining = []
    for m in user_msgs:
        if m.get('expire_at') and m['expire_at'] < now:
            # skip expired (do not deliver)
            continue
        deliver.append(m)
    # delete delivered messages (auto-destruct)
    messages[user_id] = []
    return {'messages': deliver}

async def _purge_expired_loop():
    while True:
        now = time.time()
        for user_id, msg_list in list(messages.items()):
            new_list = [m for m in msg_list if not (m.get('expire_at') and m['expire_at'] < now)]
            messages[user_id] = new_list
        await asyncio.sleep(10)

@app.on_event('startup')
async def startup_event():
    # background purge task
    asyncio.create_task(_purge_expired_loop())
