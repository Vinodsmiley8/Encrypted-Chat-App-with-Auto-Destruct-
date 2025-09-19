# Encrypted Chat App with Auto-Destruct

**Category:** Cybersecurity + Software Development  
**Purpose:** Minimal end-to-end encrypted messaging demo where messages are stored only as ciphertext on the server and are deleted (auto-destructed) immediately after retrieval.

## Components
- `server/` — FastAPI server that stores ciphertext messages and deletes them when the recipient reads them. Also supports optional TTL (expiration).
- `scripts/` — Simple command-line utilities to generate NaCl keypairs, send encrypted messages, and receive/decrypt messages.

## Security model & notes
- This is a **demo**. It demonstrates the pattern: sender encrypts with recipient's public key (and sender's private key) using NaCl Box (libsodium). The server never sees plaintext and deletes ciphertext after delivery.
- Do NOT consider this production-ready. Review key storage, authentication, transport security (HTTPS), replay protections, rate limiting, and secure deletion requirements for production use.

## Requirements
- Python 3.8+
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

## Quickstart (local)
1. Start server:
   ```
   python -m server.main
   ```
   (Runs FastAPI on http://127.0.0.1:8000)
2. Generate two keypairs (Alice and Bob):
   ```
   python scripts/generate_keys.py --name alice
   python scripts/generate_keys.py --name bob
   ```
   This creates `alice_private.key`, `alice_public.key`, etc.
3. Register public keys with server:
   ```
   curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"user_id":"alice","public_key":"<base64>"}'
   ```
   (See `scripts/register_key.py` for a helper.)
4. Send an encrypted message:
   ```
   python scripts/send_message.py --sender alice --recipient bob --private-key alice_private.key --recipient-pub bob_public.key --message "Hello Bob — this will self-destruct after read"
   ```
5. Bob receives messages (server will delete returned messages immediately):
   ```
   python scripts/receive_messages.py --user bob --private-key bob_private.key
   ```

## How auto-destruct works
- Messages are stored as ciphertext on the server.
- When a recipient requests their messages, the server returns the ciphertexts and deletes them immediately (auto-destruct after reading).
- Optionally, messages may include an `expire_at` timestamp (TTL) and will be purged by the server when expired.

## Files in repo
- `server/main.py` — FastAPI server
- `scripts/generate_keys.py` — NaCl keypair generator
- `scripts/register_key.py` — helper to register a public key with the server
- `scripts/send_message.py` — encrypt & send
- `scripts/receive_messages.py` — fetch & decrypt (auto-destruct)
- `requirements.txt`

## License
MIT (demo)
