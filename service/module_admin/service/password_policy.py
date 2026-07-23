"""密码策略与历史密码校验。"""

import string
from collections.abc import Iterable

from config.env import settings


class PasswordPolicyError(ValueError):
    """密码不符合当前安全策略。"""


def validate_password(password: str, username: str | None = None) -> None:
    """校验密码长度、复杂度和与账号的明显关联。"""
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise PasswordPolicyError(
            f"密码长度不能少于 {settings.PASSWORD_MIN_LENGTH} 个字符"
        )
    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(
        char.isupper() for char in password
    ):
        raise PasswordPolicyError("密码必须包含大写字母")
    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(
        char.islower() for char in password
    ):
        raise PasswordPolicyError("密码必须包含小写字母")
    if settings.PASSWORD_REQUIRE_DIGIT and not any(char.isdigit() for char in password):
        raise PasswordPolicyError("密码必须包含数字")
    if settings.PASSWORD_REQUIRE_SPECIAL and not any(
        char in string.punctuation for char in password
    ):
        raise PasswordPolicyError("密码必须包含特殊字符")
    if username and username.casefold() in password.casefold():
        raise PasswordPolicyError("密码不能包含用户名")


def matches_history(password: str, password_hashes: Iterable[str], verify) -> bool:
    """判断明文密码是否命中历史密码哈希。"""
    return any(verify(password, password_hash) for password_hash in password_hashes)
