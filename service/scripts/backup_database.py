"""数据库加密备份和恢复命令行入口。"""

import argparse
import asyncio

from module_admin.service.backup_service import BackupService


def main() -> None:
    """执行备份或恢复命令。"""
    parser = argparse.ArgumentParser(description="FastAPI Admin database backup")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("backup")
    restore = subparsers.add_parser("restore")
    restore.add_argument("path")
    args = parser.parse_args()
    if args.command == "backup":
        print(asyncio.run(BackupService.create_backup()))
    else:
        asyncio.run(BackupService.restore_backup(args.path))


if __name__ == "__main__":
    main()
