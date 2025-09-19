# Fetch messages for a user, decrypt with their private key. Server deletes delivered messages.
import argparse, base64, requests
from nacl.public import PrivateKey, PublicKey, Box
from nacl.exceptions import CryptoError

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='http://127.0.0.1:8000', help='server URL')
parser.add_argument('--user', required=True)
parser.add_argument('--private-key', required=True, help='path to private key (base64)')
args = parser.parse_args()

with open(args.private_key, 'r') as f:
    priv_b64 = f.read().strip()
priv = PrivateKey(base64.b64decode(priv_b64))

resp = requests.get(args.server + f'/receive/{args.user}')
if resp.status_code != 200:
    print('Error:', resp.status_code, resp.text)
    raise SystemExit(1)
data = resp.json()
msgs = data.get('messages', [])
if not msgs:
    print('No messages.')
    raise SystemExit(0)
for m in msgs:
    print('---')
    print('From:', m['sender'])
    ct = base64.b64decode(m['ciphertext_b64'])
    # To decrypt we need sender's public key. For demo try to fetch from server.
    try:
        pk_resp = requests.get(args.server + f"/public_key/{m['sender']}")
        if pk_resp.status_code == 200:
            sender_pub_b64 = pk_resp.json()['public_key_b64']
            sender_pub = PublicKey(base64.b64decode(sender_pub_b64))
            box = Box(priv, sender_pub)
            try:
                plain = box.decrypt(ct)
                print('Message:', plain.decode('utf-8'))
            except CryptoError:
                print('Failed to decrypt message (crypto error)')
        else:
            print('Sender public key not found; cannot decrypt.')
    except Exception as e:
        print('Error fetching sender public key:', e)
print('\nMessages delivered and removed from server (auto-destruct).')
