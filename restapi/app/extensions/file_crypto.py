import os
import random
import struct
import hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


class FileCrypto(object):
    def __init__(self):
        self.chunksize = 64 * 1024  # Load file in chunks, slower but requires less RAM
        self.session_key_size = 32  # 32 bytes => AES256
        self.rsa_key_size = 2048
        self.aes_mode = AES.MODE_CBC

    def encrypt_file(self, input_filepath, output_filepath, passphrase):
        """Encrypt a file with a random session_key and return privatekey to decrypt it."""
        # Init AES encryptor
        session_key = get_random_bytes(self.session_key_size)
        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(AES.block_size))
        encryptor = AES.new(session_key, self.aes_mode, iv)
        filesize = os.path.getsize(input_filepath)

        # Generate RSA public and private keys
        key = RSA.generate(self.rsa_key_size)
        encrypted_key = key.exportKey(passphrase=passphrase, pkcs=8)

        # Encrypt session_key with RSA publickey using PKCS#1 OAEP
        cipher_rsa = PKCS1_OAEP.new(key)
        encrypted_session_key = cipher_rsa.encrypt(session_key)

        with open(input_filepath, 'rb') as f:
            with open(output_filepath, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))  # Record filesize (long number)
                outfile.write(encrypted_session_key)
                outfile.write(iv)

                while True:
                    chunk = f.read(self.chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % AES.block_size != 0:
                        chunk += ' ' * (AES.block_size - len(chunk) % AES.block_size)  # Padding

                    outfile.write(encryptor.encrypt(chunk))
        return encrypted_key

    def decrypt_file(self, input_filepath, private_key, output_filepath, passphrase):
        """ Decrypt a file using AES (CBC mode) with a privatekey and passphrase."""
        with open(input_filepath, 'rb') as f:
            origsize = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
            encrypted_session_key = f.read(self.rsa_key_size // 8)
            iv = f.read(16)

            # Decrypt session key using RSA private key
            key = RSA.importKey(private_key, passphrase=passphrase)
            cipher_rsa = PKCS1_OAEP.new(key)
            session_key = cipher_rsa.decrypt(encrypted_session_key)

            # Decrypt the file with AES
            decryptor = AES.new(session_key, self.aes_mode, iv)
            with open(output_filepath, 'wb') as outfile:
                while True:
                    chunk = f.read(self.chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)