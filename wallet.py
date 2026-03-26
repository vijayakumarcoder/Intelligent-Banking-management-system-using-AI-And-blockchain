import hashlib
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

class Wallet:
    """
    Wallet System - RSA Key Pair Generation & Digital Signature
    - Public key & Private key generate pannum
    - Transaction sign pannum (digital signature)
    - Signature verify pannum
    """
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None
    
    def generate_keys(self):
        """
        RSA key pair generate pannum
        2048 bit strong encryption
        """
        key = RSA.generate(2048)
        self.private_key = key.export_key().decode('utf-8')
        self.public_key = key.publickey().export_key().decode('utf-8')
        
        # Wallet address create pannum (public key oda hash)
        self.address = self.generate_address(self.public_key)
        
        return {
            'private_key': self.private_key,
            'public_key': self.public_key,
            'address': self.address
        }
    
    def generate_address(self, public_key):
        """
        Public key ah use panni short wallet address create pannum
        SHA-256 hash oda first 20 characters edukrom
        """
        hash_object = hashlib.sha256(public_key.encode())
        return hash_object.hexdigest()[:20].upper()
    
    def sign_transaction(self, transaction_data, private_key_str):
        """
        Transaction ah private key use panni sign pannum
        Digital signature create pannum
        """
        try:
            # Private key import pannum
            private_key = RSA.import_key(private_key_str)
            
            # Transaction data ah string ah convert pannum
            transaction_string = json.dumps(transaction_data, sort_keys=True)
            
            # Hash create pannum
            hash_object = SHA256.new(transaction_string.encode('utf-8'))
            
            # Sign pannum
            signature = pkcs1_15.new(private_key).sign(hash_object)
            
            # Base64 encode panni return pannum
            return base64.b64encode(signature).decode('utf-8')
        
        except Exception as e:
            print(f"Signing error: {str(e)}")
            return None
    
    def verify_signature(self, transaction_data, signature_str, public_key_str):
        """
        Transaction signature verify pannum
        Public key use panni signature correct-ah iruka check pannum
        """
        try:
            # Public key import pannum
            public_key = RSA.import_key(public_key_str)
            
            # Transaction data string ah convert pannum
            transaction_string = json.dumps(transaction_data, sort_keys=True)
            
            # Hash create pannum
            hash_object = SHA256.new(transaction_string.encode('utf-8'))
            
            # Signature decode pannum
            signature = base64.b64decode(signature_str)
            
            # Verify pannum
            pkcs1_15.new(public_key).verify(hash_object, signature)
            return True
        
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return False
    
    @staticmethod
    def load_keys(private_key_str, public_key_str):
        """
        Existing keys ah load pannum
        User login pannum pothu use aagum
        """
        wallet = Wallet()
        wallet.private_key = private_key_str
        wallet.public_key = public_key_str
        wallet.address = wallet.generate_address(public_key_str)
        return wallet