"""后台管理通用工具。"""

import json
import base64
import random
import secrets
import os
import sys
import string
from typing import Union
from datetime import datetime
from passlib.context import CryptContext
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class FastApiAdmin:
    """FastAPI 管理后台通用工具集合。"""

    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

    class Scopes:
        """Scopes类."""

        def __init__(
            self, roles: list[Union[str, int]], permissions: list[str]
        ) -> None:
            """初始化."""
            self.roles = roles
            self.permissions = permissions

    @staticmethod
    def start_serve():
        """
        启动服务.
        :return:
        """
        print(
            r"""

                                                         __----~~~~~~~~~~~------___
                                        .  .   ~~//====......          __--~ ~~
                         -.            \_|//     |||\  ~~~~~~::::... /~
                      ___-==_       _-~o~  \/    |||  \            _/~~-
              __---~~~.==~||\=_    -_--~/_-~|-   |||   \        _/~
          _-~~     .=~    |  \-_    '-~7  /-   /  ||    \      /
        .~       .~       |   \ -_    /  /-   /   ||      \   /
       /  ____  /         |     \ ~-_/  /|- _/   .||       \ /
       |~~    ~~|--~~~~--_ \     ~==-/   | \~--===~~        .|
                '         ~-|      /|    |-~\~~       __--~~
                            |-~~-_/ |    |   ~\_   _-~            /|
                                 /  \     \__   \/~                \__
                             _--~ _/ | .-~~____--~-/                  ~~==.
                            ((->/~   '.|||' -_|    ~~-/ ,              . _||
                                       -_     ~\      ~~---l__i__i__i--~~_/
                                       _-~-__   ~)  \--______________--~~
                                     //.-~~~-~_--~- |-------~~~~~~~~
                                            //.-~~~--|


                                    神兽保佑            永无BUG
           """
        )
        sys.stdout.flush()

    @staticmethod
    def set_scopes(scopes: Scopes) -> list[str]:
        """
        设置权限.
        :param scopes:
        :return: [data]
        """
        if isinstance(scopes, FastApiAdmin.Scopes) is False:
            raise TypeError("type is not Scopes")
        scopes = scopes.__dict__
        data = json.dumps(scopes)
        return [data]

    @staticmethod
    def convert_to_datetime(date_string: str) -> datetime:
        """
        转换日期字符串为datetime类型.
        :param date_string:
        :return:
        """
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise TypeError("date_string is type error")

    @staticmethod
    def password_hash(password: str) -> str:
        """密码加密.

        Args:
            password (str): 密码.

        Returns:
            str: 加密数据.
        """
        try:
            return FastApiAdmin.pwd_context.hash(password)
        except ValueError:
            raise TypeError("password is type error")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """密码校验.

        Args:
            plain_password (str): 输入的密码.
            hashed_password (str): 加密数据.

        Returns:
            bool: 是否一致.
        """
        try:
            return FastApiAdmin.pwd_context.verify(plain_password, hashed_password)
        except ValueError:
            raise TypeError("plain_password or hashed_password is type error")

    @staticmethod
    def create_random_captcha(length: int = 4) -> str:
        """随机生成验证码
        Args:
            length (int, optional): 验证码长度. Defaults to 4.

        Returns:
            str: 验证码
        """
        return "".join(secrets.choice(string.digits) for _ in range(length))

    class CaptchaGenerator:
        """验证码生成器.

        Returns:
            _type_: _description_
        """

        def __init__(
            self, code: str, width: int = 128, height: int = 30, font_size: int = 25
        ):
            """初始化.

            Args:
                width (int): 验证码图片宽度
                height (int): 验证码图片高度
                code (str): 验证码
                font_size (int): 验证码文字大小
            """
            self.width = width
            self.height = height
            self.code = code
            self.font_size = font_size
            self.line_color = (
                random.randint(0, 128),
                random.randint(0, 128),
                random.randint(0, 128),
            )
            self.dot_color = (
                random.randint(0, 128),
                random.randint(0, 128),
                random.randint(0, 128),
            )
            self.font_color = (
                random.randint(0, 128),
                random.randint(0, 128),
                random.randint(0, 128),
            )

        async def create_captcha(self) -> str:
            """创建验证码

            Args:
                code (str | int): 验证码-建议使用4位验证码.

            Returns:
                str: 验证码.
            """
            # 绘制空白图片背景
            image = Image.new("RGB", (self.width, self.height), color="#F6F8FA")
            # 创建图片对象
            draw = ImageDraw.Draw(image)
            # 创建字体对象
            font = ImageFont.truetype(
                os.path.join(
                    os.path.abspath(os.getcwd()), "assets", "font", "AlimamaDaoLiTi.ttf"
                ),
                size=self.font_size,
            )
            # 绘制干扰点
            for i in range(100):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                draw.point((x, y), fill=self.dot_color)
            # 绘制干扰线
            for i in range(3):
                x1 = random.randint(0, self.width)
                y1 = random.randint(0, self.height)
                x2 = random.randint(0, self.width)
                y2 = random.randint(0, self.height)
                draw.line((x1, y1, x2, y2), fill=self.line_color, width=3)
            # 绘制验证码
            draw.text((30, 0), text=self.code, fill="#000", font=font)
            # 创建io
            img_byte_arr = BytesIO()
            # 保存图片
            image.save(img_byte_arr, format="PNG")
            # 转换为base64
            base64_string = base64.b64encode(img_byte_arr.getvalue()).decode()
            return f"data:image/png;base64,{base64_string}"

    @staticmethod
    def creact_random_string(length: int = 4) -> str:
        """随机生成指定长度的字符串.

        Args:
            length (int, optional): 字符串长度. Defaults to 4.

        Returns:
            str: 随机字符串.
        """
        chars = string.ascii_letters + string.digits  # 包含大小写字母和数字
        return "".join(random.choices(chars, k=length))

    @staticmethod
    def get_file(file_path: str) -> str:
        """获取文件.
        Args:
            file_path (str): 文件相对路径.
            Returns:
            str: 文件内容.
        """
        try:
            file = os.path.abspath(file_path)
            with open(file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"{file} not found")
        except Exception as e:
            raise e

    @staticmethod
    def create_three(data: list, id_field: str = "id", parent_field: str = "parent_id"):
        """
        构建树形结构.
        :param data: 数据列表.
        :param id_field: 主键字段.
        :param parent_field: 父级字段.
        :return: 树形结构列表.
        """
        tree = []
        nodes = []
        for item in data:
            if isinstance(item, dict):
                node = item.copy()
            elif callable(getattr(item, "model_dump", None)):
                node = item.model_dump()
            else:
                node = {
                    key: value
                    for key, value in vars(item).items()
                    if not key.startswith("_")
                }
            node["children"] = []
            nodes.append(node)

        items_dict = {node[id_field]: node for node in nodes}
        for node in nodes:
            node_id = node[id_field]
            parent_id = node.get(parent_field)
            parent = items_dict.get(parent_id)
            if parent is None or parent_id == node_id:
                tree.append(node)
            else:
                parent["children"].append(node)
        return tree
