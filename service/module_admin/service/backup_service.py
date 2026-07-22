"""MySQL 加密备份和恢复服务。"""

import asyncio
import base64
import hashlib
import os
import subprocess
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi import HTTPException

from config.env import PROJECT_ROOT, Settings, settings


class BackupService:
    """使用 mysqldump/mysql 完成加密备份和受控恢复。"""

    @staticmethod
    def _settings(app_settings: Settings | None = None) -> Settings:
        return app_settings or settings

    @classmethod
    def _root(cls, app_settings: Settings) -> Path:
        root = Path(app_settings.BACKUP_DIR)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        return root.resolve()

    @classmethod
    def _fernet(cls, app_settings: Settings) -> Fernet:
        if app_settings.BACKUP_ENCRYPTION_KEY:
            try:
                return Fernet(app_settings.BACKUP_ENCRYPTION_KEY.encode("ascii"))
            except (ValueError, TypeError) as exc:
                raise HTTPException(status_code=500, detail="备份加密密钥无效") from exc
        derived = base64.urlsafe_b64encode(
            hashlib.sha256(
                (app_settings.SECRET_KEY + ":database-backup").encode("utf-8")
            ).digest()
        )
        return Fernet(derived)

    @classmethod
    async def create_backup(cls, app_settings: Settings | None = None) -> Path:
        """创建加密数据库备份并清理过期文件。"""
        app_settings = cls._settings(app_settings)
        root = cls._root(app_settings)
        root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target = root / f"fastapi-admin-{timestamp}.sql.enc"
        env = os.environ.copy()
        env["MYSQL_PWD"] = app_settings.MYSQL_PASSWORD
        command = [
            "mysqldump",
            "--protocol=tcp",
            "--host",
            app_settings.MYSQL_HOST,
            "--port",
            str(app_settings.MYSQL_POST),
            "--user",
            app_settings.MYSQL_USERNAME,
            "--single-transaction",
            "--routines",
            "--events",
            app_settings.MYSQL_DATABASES,
        ]
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                env=env,
                capture_output=True,
                check=True,
                timeout=app_settings.BACKUP_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise HTTPException(status_code=503, detail="数据库备份失败") from exc
        target.write_bytes(cls._fernet(app_settings).encrypt(result.stdout))
        cls._cleanup(root, app_settings)
        return target

    @classmethod
    async def restore_backup(
        cls, backup_path: str, app_settings: Settings | None = None
    ) -> None:
        """仅从备份目录内的加密文件恢复数据库。"""
        app_settings = cls._settings(app_settings)
        root = cls._root(app_settings)
        candidate = Path(backup_path)
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        if candidate.parent != root or candidate.suffix != ".enc" or not candidate.is_file():
            raise HTTPException(status_code=400, detail="备份文件路径无效")
        try:
            dump = cls._fernet(app_settings).decrypt(candidate.read_bytes())
        except Exception as exc:
            raise HTTPException(status_code=400, detail="备份文件无法解密") from exc
        env = os.environ.copy()
        env["MYSQL_PWD"] = app_settings.MYSQL_PASSWORD
        command = [
            "mysql",
            "--protocol=tcp",
            "--host",
            app_settings.MYSQL_HOST,
            "--port",
            str(app_settings.MYSQL_POST),
            "--user",
            app_settings.MYSQL_USERNAME,
            app_settings.MYSQL_DATABASES,
        ]
        try:
            await asyncio.to_thread(
                subprocess.run,
                command,
                input=dump,
                env=env,
                capture_output=True,
                check=True,
                timeout=app_settings.BACKUP_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise HTTPException(status_code=503, detail="数据库恢复失败") from exc

    @staticmethod
    def _cleanup(root: Path, app_settings: Settings) -> None:
        cutoff = datetime.now().timestamp() - app_settings.BACKUP_RETENTION_DAYS * 86400
        for path in root.glob("*.sql.enc"):
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
