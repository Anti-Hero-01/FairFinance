"""
Field-level encryption service using AES-256
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from backend.config.settings import settings

class EncryptionService:
    def __init__(self):
        # Load key from settings
        key = settings.ENCRYPTION_KEY.encode()

        # Derive a proper 32-byte key for Fernet if needed
        if len(key) < 32:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fairfinance_salt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
        else:
            key = base64.urlsafe_b64encode(key[:32])

        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        if data is None:
            return None
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        if encrypted_data is None:
            return None
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """Encrypt specific fields in dictionary"""
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field] is not None:
                encrypted[field] = self.encrypt(str(encrypted[field]))
        return encrypted

    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """Decrypt specific fields in dictionary"""
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field] is not None:
                decrypted[field] = self.decrypt(decrypted[field])
        return decrypted


# Global encryption service
encryption_service = EncryptionService()

# Fields to encrypt
PROTECTED_FIELDS = ['gender', 'region', 'age_group', 'income']
