#!/usr/bin/env python3
"""
Token encryption/decryption manager for secure token storage in repository.
Uses Fernet symmetric encryption with a key stored in GitHub Secrets.
"""

import os
import sys
import json
from pathlib import Path
from cryptography.fernet import Fernet


class TokenManager:
    """Manages encryption and decryption of Google OAuth tokens."""

    def __init__(self, encryption_key=None):
        """
        Initialize the token manager.

        Args:
            encryption_key: Base64-encoded Fernet key (from environment or generated)
        """
        if encryption_key:
            self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        else:
            # Generate a new key if none provided
            self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    def encrypt_token(self, token_data):
        """
        Encrypt token data.

        Args:
            token_data: Dictionary or JSON string containing token

        Returns:
            Encrypted token as bytes
        """
        if isinstance(token_data, dict):
            token_data = json.dumps(token_data)

        if isinstance(token_data, str):
            token_data = token_data.encode()

        return self.cipher.encrypt(token_data)

    def decrypt_token(self, encrypted_data):
        """
        Decrypt token data.

        Args:
            encrypted_data: Encrypted token bytes

        Returns:
            Decrypted token as dictionary
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()

        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

    def save_encrypted_token(self, token_file, output_file):
        """
        Read a plain token file and save encrypted version.

        Args:
            token_file: Path to plain token.json
            output_file: Path to save encrypted token
        """
        with open(token_file, 'r') as f:
            token_data = f.read()

        encrypted = self.encrypt_token(token_data)

        with open(output_file, 'wb') as f:
            f.write(encrypted)

        print(f"✓ Token encrypted and saved to {output_file}")

    def save_decrypted_token(self, encrypted_file, output_file):
        """
        Read an encrypted token file and save decrypted version.

        Args:
            encrypted_file: Path to encrypted token file
            output_file: Path to save decrypted token.json
        """
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()

        token_data = self.decrypt_token(encrypted_data)

        with open(output_file, 'w') as f:
            json.dump(token_data, f, indent=2)

        print(f"✓ Token decrypted and saved to {output_file}")

    def get_key_string(self):
        """Get the encryption key as a string for storage in GitHub Secrets."""
        return self.key.decode()


def main():
    """CLI interface for token management."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Generate new encryption key:")
        print("    python token_manager.py generate-key")
        print()
        print("  Encrypt token:")
        print("    python token_manager.py encrypt <token.json> <output-file> <encryption-key>")
        print()
        print("  Decrypt token:")
        print("    python token_manager.py decrypt <encrypted-file> <token.json> <encryption-key>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate-key":
        key = Fernet.generate_key().decode()
        print("=" * 70)
        print("NEW ENCRYPTION KEY (save this in GitHub Secrets as TOKEN_ENCRYPTION_KEY):")
        print("=" * 70)
        print(key)
        print("=" * 70)
        print()
        print("IMPORTANT: Save this key securely!")
        print("1. Copy the key above")
        print("2. Go to GitHub Settings → Secrets → Actions")
        print("3. Create new secret: TOKEN_ENCRYPTION_KEY")
        print("4. Paste the key")
        print()

    elif command == "encrypt":
        if len(sys.argv) != 5:
            print("Error: encrypt requires <input-file> <output-file> <encryption-key>")
            sys.exit(1)

        input_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4]

        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found")
            sys.exit(1)

        manager = TokenManager(key)
        manager.save_encrypted_token(input_file, output_file)

    elif command == "decrypt":
        if len(sys.argv) != 5:
            print("Error: decrypt requires <input-file> <output-file> <encryption-key>")
            sys.exit(1)

        input_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4]

        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found")
            sys.exit(1)

        manager = TokenManager(key)
        manager.save_decrypted_token(input_file, output_file)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
