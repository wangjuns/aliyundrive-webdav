import logging
import os
from datetime import datetime
from typing import List

from wsgidav import util

from drive.cache import Cache
from drive.drive import AliyunDrive
from drive.model import FileItem, GetDownloadUrlResponse
from util import ROOT_DIR
from cachetools import cached, TTLCache, FIFOCache

logger = logging.getLogger('aliyundrive-dav')
cache_dir = os.path.join(ROOT_DIR, 'cache')
cache_path = os.path.join(cache_dir, 'data')
downurl_cache = TTLCache(maxsize=100000, ttl=3600)
file_list_chache = TTLCache(maxsize=100000, ttl=36000)
file_item_cache = FIFOCache(maxsize=100000)


class AliyunDriveAdapter():

    def __init__(self) -> None:
        self.drive = AliyunDrive()
        self.cache = Cache()
        # atexit.register(self.close)

    def get_item_by_path(self, path: str) -> FileItem:
        """
        根据路径获取file_item
        """
        assert path.startswith('/') and path != '/'
        return self.get_file_item(path)

    def get_file_list_by_path(self, path: str) -> List[FileItem]:
        """
        根据路径获取文件列表
        """
        assert path.startswith('/') and path.endswith('/')

        uri_parent = util.get_uri_parent(path)
        if uri_parent is None:
            return self._get_file_list('root')

        item = self.get_file_item(path)

        if item is not None:
            return self._get_file_list(item.file_id)
        else:
            return []
        

    @cached(cache=file_item_cache)
    def get_file_item(self, path: str) -> FileItem:
        parents = path.rstrip('/').split('/')
        target = parents[-1]
        parents = parents[:-1]

        file_items = []
        full_path = ""
        for name in parents:
            if name == '':
                file_items = self._get_file_list('root')
            else:
                t_path = f"{full_path}/{name}"
                item: FileItem = next(x for x in file_items if x.name == name)
                assert item is not None
                file_items = self._get_file_list(item.file_id)
                full_path = t_path

        return next(x for x in file_items if x.name == target)

    @cached(cache=file_list_chache)
    def _get_file_list(self, file_id: str) -> List[FileItem]:
        return [x for x in self.drive.list_all_files(file_id)]

    def get_downurl(self, file_id: str) -> str:
        """
        获取文件下载链接
        """
        resp = self.get_downurl_with_cache(file_id)
        if resp.expiration.timestamp() < datetime.now().timestamp() + 3600:
            downurl_cache.pop(file_id)
            resp = self.get_downurl_with_cache(file_id)

        logger.debug("resp %s" % resp)
        return self.get_file_url(resp)

    @cached(cache=downurl_cache)
    def get_downurl_with_cache(self, file_id: str) -> GetDownloadUrlResponse:
        return self.get_downurl_without_cache(file_id)

    def get_downurl_without_cache(self, file_id: str) -> GetDownloadUrlResponse:
        return self.drive.get_file_download_url(file_id)

    def get_file_url(self, resp: GetDownloadUrlResponse) -> str:
        if resp.cdn_url is not None:
            return resp.cdn_url
        else:
            return resp.url
