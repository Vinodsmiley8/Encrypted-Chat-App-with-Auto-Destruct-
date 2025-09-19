# Helper to register a public key with the server
import argparse, base64, json, requests

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='http://127.0.0.1:8000', help='server base URL')
parser.add_argument('--user', required=True, help='user id to register')
parser.add_argument('--pubkey', required=True, help='path to public key (base64)')
args = parser.parse_args()

with open(args.pubkey, 'r') as f:
    pub_b64 = f.read().strip()
payload = {'user_id': args.user, 'public_key_b64': pub_b64}
resp = requests.post(args.server + '/register', json=payload)
print(resp.status_code, resp.text)
