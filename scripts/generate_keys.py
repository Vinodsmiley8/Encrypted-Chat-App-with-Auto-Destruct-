# Generate NaCl keypair (PyNaCl) and save to files
import argparse
import base64
from nacl.public import PrivateKey

parser = argparse.ArgumentParser(description='Generate NaCl keypair')
parser.add_argument('--name', required=True, help='name prefix for key files')
args = parser.parse_args()

priv = PrivateKey.generate()
pub = priv.public_key

priv_b64 = base64.b64encode(priv.encode()).decode('ascii')
pub_b64 = base64.b64encode(pub.encode()).decode('ascii')

priv_path = f"{args.name}_private.key"
pub_path = f"{args.name}_public.key"
with open(priv_path, 'w') as f:
    f.write(priv_b64)
with open(pub_path, 'w') as f:
    f.write(pub_b64)
print(f"Wrote {priv_path} and {pub_path}")
