#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''


from apps.config.schema import ConfigSchema, PasswordPolicySchema
from .schema import RSASchema, RecoverySchema
from Crypto.Random import get_random_bytes
from apps.auth.schema import LoggedUser
from Crypto.Cipher import PKCS1_OAEP
from .exceptions import InvalidPassphrase
from apps.config.models import Config
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from settings import settings
import logging.config
import logging
import random
import hashlib
import base64
import secrets
import string
import json

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class CryptoUtils:
    @staticmethod
    def prepare_password(password: str) -> str:
        """Prepare password to be used as RSA Passphrase

        Args:
            password (str): user password

        Returns:
            str: sha512 of user's password
        """
        sha512_password: str = hashlib.sha512(
            password.encode()
        ).hexdigest()

        return sha512_password

    @staticmethod
    def _unpad(s) -> str:
        return s[:-ord(s[len(s) - 1:])]

    @classmethod
    def decrypt_password(cls, user: LoggedUser) -> str:
        """Decrypt user password

        Args:
            user (LoggedUser): user information

        Returns:
            str: password
        """
        return cls.sym_decrypt(json.loads(user.encrypted_password), user.session_key)

    @classmethod
    def generate_rsa_keys(cls, password: str) -> RSASchema:
        """Generate pair RSA Keys

        Args:
            password (str): User's password

        Returns:
            RSASchema: RSA Pub & Priv keys
        """
        password: str = cls.prepare_password(password)
        
        if not isinstance(password, bytes):
            password = bytes(password, "utf-8")

        config: ConfigSchema = Config.objects.get().to_schema()
        key = RSA.generate(config.rsa_key_size, Random.new().read)
        pubkey = key.publickey().exportKey().decode("utf-8")
        privkey = key.exportKey(passphrase=password).decode("utf-8")
        return RSASchema(
            pubkey=pubkey,
            privkey=privkey
        )

    @classmethod
    def generate_sim(cls, length: int = 32) -> str:
        """Generate symmetric key
        """
        letters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for i in range(length))
    
    @classmethod
    def generate_recovery_symkey(cls, user: LoggedUser, pwd: str | None=None) -> RecoverySchema:
        if pwd is None:
            pwd: str = cls.decrypt_password(user)

        sym_key: str = cls.generate_sim()
        encoded_sym_key: str = base64.b64encode(bytes(sym_key, 'utf-8')).decode('utf-8')
        encrypted_password: str = cls.sym_encrypt(pwd, sym_key)

        return RecoverySchema(
            encrypted_password=encrypted_password,
            encoded_sym_key=encoded_sym_key
        )

    @classmethod
    def sym_encrypt(cls, message: str, key: str | bytes) -> str:
        """Encrypt message with symmetric key

        Args:
            message (str): Message to encrypt
            key (str): Symmetric key

        Returns:
            str: Encrypted message
        """
        if message == "":
            return message

        if not isinstance(key, bytes):
            key: bytes = key.encode('utf-8')
        
        if not isinstance(message, bytes):
            message: bytes = message.encode("utf-8")

        cipher = AES.new(key, AES.MODE_GCM)
        header: bytes = get_random_bytes(16)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(message)
        json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
        json_v = [ base64.b64encode(x).decode('utf-8') for x in [cipher.nonce, header, ciphertext, tag ]]
        message = json.dumps(dict(zip(json_k, json_v)))
        return message
    
    @classmethod
    def sym_decrypt(cls, message: str, key: str | bytes, mode: str = "GCM") -> str:
        """Decrypt message with symmetric key

        Args:
            message (str): Message to be decrypted
            key (str): Symmetric key

        Returns:
            str: Decrypted message
        """
        if message == "":
            return message

        if not isinstance(key, bytes):
            key = key.encode('utf-8')

        if mode == "GCM":
            b64 = json.loads(message)

            json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
            jv = {k: base64.b64decode(b64[k]) for k in json_k}

            cipher = AES.new(key, AES.MODE_GCM, nonce=jv["nonce"])
            cipher.update(jv["header"])
            text = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
            return text
        else:
            message = base64.b64decode(message)
            iv = message[:AES.block_size]

            cipher = AES.new(key, AES.MODE_CBC, iv)
            text = cls._unpad(cipher.decrypt(message[AES.block_size:]))
            return text.decode('utf-8')

    @classmethod
    def rsa_encrypt(cls, message: str, pubkey: str) -> str:
        """Encrypt Message with RSA Public Key

        Args:
            message (str): Message to be encrypted
            pubkey (str): User RSA public key

        Returns:
            str: Encrypted message
        """
        rsa = RSA.import_key(pubkey)
        pkc = PKCS1_OAEP.new(rsa)

        encrypted_message = pkc.encrypt(bytes(message, "utf-8"))
        b64_encrypted_message = base64.b64encode(encrypted_message)
        return b64_encrypted_message.decode("utf-8")

    @classmethod
    def rsa_decrypt(cls, encrypted_message: str, privkey: str, passphrase: str) -> str:
        """Decrypt message with RSA Private key

        Args:
            encrypted_message (str): Encrypted message
            privkey (str): User's Private Key
            passphrase (str): User's Passphrase

        Raises:
            InvalidPassphrase: Invalid passphrase

        Returns:
            str: Decrypted message
        """
        try:
            rsa = RSA.import_key(privkey, passphrase=passphrase)
            pkc = PKCS1_OAEP.new(rsa)
            message: str = pkc.decrypt(base64.b64decode(encrypted_message))
            return message.decode("utf-8")

        except ValueError as err:
            logger.critical(err, exc_info=1)
            raise InvalidPassphrase()

    @classmethod
    def generate_password(cls, password_policy: PasswordPolicySchema|None):        
        # TODO: Enhance this method to generate stronger password
        def generate(min_length: int, chars_to_use: str) -> list[str]:
            return [secrets.choice(chars_to_use) for i in range(min_length)]

        min_length: int = 12
        password: str = ""

        chars: dict = {
            "lowercase": string.ascii_lowercase,
            "uppercase": string.ascii_uppercase,
            "special": string.punctuation,
            "numbers": string.digits,
        }

        if password_policy is None:
            chars_to_use = "".join(chars.values())
            password: list[str] = generate(min_length, chars_to_use)
        else:
            min_length: int = password_policy.length

            password: list[str] = generate(password_policy.special, chars["special"])
            password.extend(generate(password_policy.numbers, chars["numbers"]))
            password.extend(generate(password_policy.uppercase, chars["uppercase"]))
            password.extend(generate(password_policy.length - len(password), chars["lowercase"]))

        random.SystemRandom().shuffle(password)
        return "".join(password)
