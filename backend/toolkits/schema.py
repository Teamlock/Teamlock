from pydantic import BaseModel


class RSASchema(BaseModel):
    pubkey: str
    privkey: str


class RecoverySchema(BaseModel):
    encrypted_password: str
    encoded_sym_key: str
