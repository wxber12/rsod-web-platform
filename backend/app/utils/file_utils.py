import os
import shutil
import uuid
from fastapi import UploadFile
from app.config import settings


def ensure_directories():
    """
    检查并创建必要的静态文件目录
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)


async def save_upload_file(file: UploadFile, upload_dir: str) -> str:
    """
    保存前端上传的文件，生成唯一文件名防止冲突
    """
    # 提取文件后缀 (例如: .jpg, .png)
    _, extension = os.path.splitext(file.filename)

    # 使用 uuid 生成唯一的文件名，比如: temp_abc123.jpg
    filename = f"temp_{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(upload_dir, filename)

    # 将上传的文件流写入本地磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename


def get_file_url(filename: str, directory: str) -> str:
    """
    生成可以直接在浏览器中访问的 URL 路径
    """
    # 确保路径以 / 开头，以便前端能够正确拼接根域名
    # 例如将 "static/uploads" 和 "a.jpg" 拼接为 "/static/uploads/a.jpg"
    return f"/{directory}/{filename}"