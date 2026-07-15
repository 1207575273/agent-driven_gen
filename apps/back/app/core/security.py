"""密码哈希工具(占位)。

母版是极简种子, 不含完整鉴权。这里用标准库 pbkdf2 提供一对可用的
哈希/校验函数, 作为团队接入鉴权时的起点; 生产环境请替换为 argon2 / bcrypt。
"""

import hashlib
import hmac
import os

_ALGO = "sha256"
_ITERATIONS = 200_000
_SALT_BYTES = 16


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    salt = salt if salt is not None else os.urandom(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(_ALGO, password.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt_hex, digest_hex = hashed.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = hashlib.pbkdf2_hmac(_ALGO, password.encode(), salt, _ITERATIONS)
    return hmac.compare_digest(expected.hex(), digest_hex)
