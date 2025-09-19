# Encrypt with sender private key and recipient public key using NaCl Box, then POST to server
import argparse, base64, requests
from nacl.public import PrivateKey, PublicKey, Box

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='http://127.0.0.1:8000', help='server URL')
parser.add_argument('--sender', required=True)
parser.add_argument('--recipient', required=True)
parser.add_argument('--private-key', required=True, help='path to sender private key (base64)')
parser.add_argument('--recipient-pub', required=True, help='path to recipient public key (base64)')
parser.add_argument('--message', required=True)
parser.add_argument('--ttl', type=int, default=None, help='optional TTL seconds')
args = parser.parse_args()

with open(args.private_key, 'r') as f:
    priv_b64 = f.read().strip()
with open(args.recipient_pub, 'r') as f:
    rec_b64 = f.read().strip()
priv = PrivateKey(base64.b64decode(priv_b64))
rec_pub = PublicKey(base64.b64decode(rec_b64))
box = Box(priv, rec_pub)
encrypted = box.encrypt(args.message.encode('utf-8'))
ct_b64 = base64.b64encode(encrypted).decode('ascii')
payload = {
    'sender': args.sender,
    'recipient': args.recipient,
    'ciphertext_b64': ct_b64
}
if args.ttl:
    payload['ttl_seconds'] = args.ttl
resp = requests.post(args.server + '/send', json=payload)
print(resp.status_code, resp.text)
