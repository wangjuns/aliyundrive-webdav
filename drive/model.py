from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    expire_time: datetime
    token_type: str
    access_token: str
    default_drive_id: str
    refresh_token: str
    user_id: str
    nick_name: str


class ListFileRequest(BaseModel):
    drive_id: str
    parent_file_id: str
    limit: int
    all: bool
    image_thumbnail_process: str
    image_url_process: str
    video_thumbnail_process: str
    fields: str
    order_by: str
    order_direction: str
    marker: Optional[str] = None


class FileItem(BaseModel):
    file_id: str
    name: str
    type: str
    mime_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    size: Optional[int] = None
    url: Optional[str] = None

    # for encrypted file
    encryption_mode: Optional[str] = None


class ListFileResponse(BaseModel):
    items: List[FileItem]
    next_marker: str


class GetDownloadUrlRequest(BaseModel):
    drive_id: str
    file_id: str
    expire_sec: Optional[int] = None


class GetDownloadUrlResponse(BaseModel):
    method: str
    url: str
    cdn_url: Optional[str] = None
    expiration: datetime
    size: int
    crc64_hash: str
    content_hash: str
    content_hash_name: str
