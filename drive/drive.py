import logging
import os
import threading
from datetime import datetime
from json import dumps
from typing import Optional

from util import ADRIVE_REQ_HEADERS, ROOT_DIR, requests_retry_session

from drive.model import (GetDownloadUrlRequest, GetDownloadUrlResponse,
                         ListFileRequest, ListFileResponse, TokenResponse)

logger = logging.getLogger('aliyundrive-dav')
refresh_token_path = os.path.join(ROOT_DIR, 'refresh_token')


class AliyunDrive():
    refresh_token_url = 'https://api.aliyundrive.com/token/refresh'
    list_file_url = 'https://api.aliyundrive.com/adrive/v3/file/list'
    get_download_url = 'https://api.aliyundrive.com/v2/file/get_download_url'

    def __init__(self, refresh_token: Optional[str] = None) -> None:
        self.token: Optional[TokenResponse] = None
        self.session = requests_retry_session()
        self.session.headers.update(ADRIVE_REQ_HEADERS)
        self.lock = threading.Lock()

        if refresh_token:
            self.refresh_token = refresh_token
        else:
            refresh_token_env = os.getenv("REFRESH_TOKEN")
            
            assert refresh_token_env is not None, "Must set REFRESH_TOKEN env"
            logger.info(f"using REFRESH_TOKEN ({refresh_token_env}) in os env")
            with open(refresh_token_path, 'w', encoding='utf8') as f:
                f.write(refresh_token_env)
                f.flush()
    
            self.refresh_token = refresh_token_env

        self._count_request = 0

    @property
    def refresh_token(self) -> str:
        if self.token:
            return self.token.refresh_token
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        assert value, 'refresh_token must not be empty'
        self._refresh_token = value
        with open(refresh_token_path, 'w', encoding='utf8') as f:
            f.write(self._refresh_token)

    def get_token(self) -> TokenResponse:
        with self.lock:
            if self.token and self.token.expire_time.timestamp() > datetime.now().timestamp() + 300:
                return self.token

            # 刷新token
            body = {'refresh_token': self.refresh_token}
            data = self._request(
                'POST', self.refresh_token_url, json=body).json()
            self.token = TokenResponse(**data)
            self.refresh_token = self.token.refresh_token
            return self.token

    def list_files(self, parent_file_id: str, marker: Optional[str] = None) -> ListFileResponse:
        token = self.get_token()
        body = ListFileRequest(
            drive_id=token.default_drive_id,
            parent_file_id=parent_file_id,
            limit=100,
            all=False,
            image_thumbnail_process='image/resize,w_400/format,jpeg',
            image_url_process='image/resize,w_1920/format,jpeg',
            video_thumbnail_process='video/snapshot,t_0,f_jpg,ar_auto,w_300',
            fields='*',
            order_by='name',
            order_direction='ASC',
            marker=marker
        ).dict(exclude_none=True)
        auth_header = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        data = self._request('POST', self.list_file_url,
                             json=body, headers=auth_header).json()
        return ListFileResponse(**data)

    def list_all_files(self, parent_file_id: str):
        marker = ''
        while True:
            resp = self.list_files(parent_file_id, marker)
            marker = resp.next_marker
            yield from resp.items
            if not marker:
                break

    def get_file_download_url(self, file_id: str) -> GetDownloadUrlResponse:
        token = self.get_token()
        body = GetDownloadUrlRequest(
            drive_id=token.default_drive_id,
            file_id=file_id,
            expire_sec=14400
        ).dict(exclude_none=True)
        auth_header = {
            'Authorization': f'{token.token_type} {token.access_token}'
        }
        data = self._request('POST', self.get_download_url,
                             json=body, headers=auth_header).json()
        return GetDownloadUrlResponse(**data)

    def read_bytes(self, url: str, n: int):
        headers = {'Range': f'bytes=0-{n}'}
        return self._request('GET', url, headers=headers)

    def _request(
        self,
        method: str,
        url: str,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        self._count_request += 1
        logger.debug(f'count_request: {self._count_request}')
        logger.debug(
            f'{method.upper()} {url}{" - " + dumps(json) if json else ""}')
        with self.session.request(method, url, json=json, headers=headers) as r:
            if r.status_code >= 400:
                raise Exception(f'{r.status_code} {r.text}')
            return r
