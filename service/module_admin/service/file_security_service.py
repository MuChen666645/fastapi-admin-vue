"""文件内容识别和病毒扫描。"""

import asyncio
import re
import struct
from pathlib import Path

from fastapi import HTTPException

from config.env import Settings


class FileSecurityService:
    """按文件签名识别内容，并可接入 ClamAV。"""

    _SIGNATURES = {
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".gif": (b"GIF87a", b"GIF89a"),
        ".webp": (b"RIFF",),
        ".pdf": (b"%PDF-",),
        ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
        ".docx": (b"PK\x03\x04",),
        ".xls": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
        ".xlsx": (b"PK\x03\x04",),
        ".zip": (b"PK\x03\x04",),
        ".txt": (b"",),
        ".csv": (b"",),
        ".json": (b"",),
    }

    @classmethod
    def redact_text(cls, content: bytes, app_settings: Settings) -> bytes:
        """对文本类文件中的手机号、邮箱和银行卡号执行脱敏。"""
        if not app_settings.FILE_REDACTION_ENABLED:
            raise HTTPException(status_code=503, detail="文件脱敏未启用")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400, detail="仅支持 UTF-8 文本文件脱敏"
            ) from exc
        for pattern in app_settings.FILE_SENSITIVE_PATTERNS:
            text = re.sub(pattern, "[REDACTED]", text)
        return text.encode("utf-8")

    @classmethod
    def validate_signature(
        cls,
        original_name: str,
        sample: bytes,
        content_type: str | None,
        app_settings: Settings,
    ) -> None:
        """拒绝空内容、扩展名与文件头不匹配及明显 MIME 欺骗。"""
        if not app_settings.FILE_CONTENT_SNIFF_ENABLED:
            return
        extension = Path(original_name).suffix.lower()
        signatures = cls._SIGNATURES.get(extension)
        if not signatures or not any(
            sample.startswith(signature) for signature in signatures
        ):
            raise HTTPException(status_code=400, detail="文件内容与扩展名不匹配")
        if extension == ".webp" and sample[8:12] != b"WEBP":
            raise HTTPException(status_code=400, detail="文件内容与扩展名不匹配")
        declared = (content_type or "").lower()
        expected_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
        }
        expected = expected_types.get(extension)
        if (
            expected
            and declared
            and declared not in {expected, "application/octet-stream"}
        ):
            raise HTTPException(status_code=400, detail="文件 MIME 类型不匹配")

    @classmethod
    async def scan_path(cls, path: Path, app_settings: Settings) -> None:
        """通过 ClamAV INSTREAM 协议扫描本地文件。"""
        if not app_settings.FILE_VIRUS_SCAN_ENABLED:
            return
        reader, writer = await asyncio.open_connection(
            app_settings.CLAMAV_HOST,
            app_settings.CLAMAV_PORT,
        )
        try:
            writer.write(b"zINSTREAM\0")
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    writer.write(struct.pack(">I", len(chunk)) + chunk)
                    await writer.drain()
            writer.write(struct.pack(">I", 0))
            await writer.drain()
            result = await reader.read(4096)
            if b"FOUND" in result or b"ERROR" in result:
                raise HTTPException(status_code=400, detail="文件安全扫描未通过")
        finally:
            writer.close()
            await writer.wait_closed()

    @classmethod
    async def scan_bytes(cls, content: bytes, app_settings: Settings) -> None:
        """扫描 OSS 上传前暂存的文件内容。"""
        if not app_settings.FILE_VIRUS_SCAN_ENABLED:
            return
        reader, writer = await asyncio.open_connection(
            app_settings.CLAMAV_HOST,
            app_settings.CLAMAV_PORT,
        )
        try:
            writer.write(b"zINSTREAM\0")
            for offset in range(0, len(content), 1024 * 1024):
                chunk = content[offset : offset + 1024 * 1024]
                writer.write(struct.pack(">I", len(chunk)) + chunk)
                await writer.drain()
            writer.write(struct.pack(">I", 0))
            await writer.drain()
            result = await reader.read(4096)
            if b"FOUND" in result or b"ERROR" in result:
                raise HTTPException(status_code=400, detail="文件安全扫描未通过")
        finally:
            writer.close()
            await writer.wait_closed()
