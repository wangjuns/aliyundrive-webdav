import os
from typing import Optional

from drive.model import FileItem

encryption_mode = (os.path.splitext(
    os.path.basename(__file__))[0]).rstrip('_check')
_supported_tar_video_exts = ['.mp4.tar', '.mkv.tar']


def check(file_item: FileItem) -> Optional[FileItem]:
    is_tar_video = any(file_item.name.endswith(ext)
                       for ext in _supported_tar_video_exts)
    if not is_tar_video:
        return None

    # 复制原file_item，修改属性不影响原file_item。也可以直接修改原file_item，返回None
    copied = file_item.copy()
    # 使用不同的名字防止冲突
    copied.name = f'[TAR]{file_item.name.rstrip(".tar")}'
    # 不要忘记赋值encryption_mode
    copied.encryption_mode = encryption_mode
    return copied
