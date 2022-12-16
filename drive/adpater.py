import atexit
from datetime import datetime
import json
import logging
import os
import shelve
import threading
from typing import List, Optional

from wsgidav import util

from drive.drive import AliyunDrive
from drive.model import FileItem, GetDownloadUrlResponse
from util import ROOT_DIR

logger = logging.getLogger('aliyundrive-dav')
cache_dir = os.path.join(ROOT_DIR, 'cache')
cache_path = os.path.join(cache_dir, 'data')


class AliyunDriveAdapter():

    def __init__(self) -> None:
        self.drive = AliyunDrive()
        self.lock = threading.Lock()
        self._load_cache()
        # atexit.register(self.close)

    def _load_cache(self):
        """
        打开缓存文件流
        """
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        self.cache = {}

    def close(self):
        """
        关闭缓存文件流
        """
        self.cache.close()

    def _key(self, key: str, group: Optional[str] = None):
        return f'{group}.{key}' if group else key

    def readCache(self, key: str, group: Optional[str] = None):
        obj = self.cache.get(self._key(key, group))
        if obj is not None:
            logger.debug("cache hitted. %s" % (self._key(key, group)))
        else:
            logger.debug("cache missing. %s" % (self._key(key, group)))
        return obj

    def putCache(self, key: str, value, group: Optional[str] = None):
        self.cache.update({self._key(key, group): value})

    def get_item_by_path(self, path: str):
        """
        根据路径获取file_item
        """
        assert path.startswith('/') and path != '/'

        file_item = self.readCache(path, "file_item")
        if file_item is not None:
            return file_item

        return self.get_file_item(path)

    def get_file_list_by_path(self, path: str) -> List[FileItem]:
        """
        根据路径获取文件列表
        """
        assert path.startswith('/') and path.endswith('/')

        uri_parent = util.get_uri_parent(path)
        if uri_parent is None:
            return self._get_file_list('/', 'root')

        item = self.readCache(path.rstrip("/"), "file_item")
        if item is None:
            item = self.get_file_item(path)

        if item is not None:
            items = self._get_file_list(path, item.file_id)

            # put item into cache
            self.put_items_in_cache(path, items)
            return items
        else:
            return []

    def put_items_in_cache(self, path: str, items: List[FileItem]):
        for i in items:
            self.putCache("%s/%s" % (path, i.name), i, "file_item")

    def get_file_item(self, path: str) -> FileItem:
        file_item = self.readCache(path, "file_item")
        if file_item is not None:
            return file_item

        parents = path.rstrip('/').split('/')
        parents = parents[:-1]

        file_items = []
        full_path = ""
        for parent in parents:
            if parent == '':
                file_items = self._get_file_list('/', 'root')
            else:
                t_path = "%s/%s" % (full_path, parent)
                item: FileItem = next(x for x in file_items if x.name == parent)
                file_items = self._get_file_list(t_path, item.file_id)
                full_path = t_path

            for item in file_items:
                self.putCache("%s/%s" % (full_path, item.name), item, "file_item")

        return self.readCache(path.rstrip('/'), "file_item")

    def _get_file_list(self, path: str, file_id: str) -> List[FileItem]:
        file_list = []

        for item in self.drive.list_all_files(file_id):
            file_list.append(item)

        return file_list

    def get_downurl(self, file_id: str) -> str:
        """
        获取文件下载链接
        """

        resp_in_cache: GetDownloadUrlResponse = self.readCache(file_id, "file_url")

        if resp_in_cache is not None:
            if resp_in_cache.expiration.timestamp() > datetime.now().timestamp() + 3600:
                return self.get_file_url(resp_in_cache)

        resp = self.drive.get_file_download_url(file_id)
        self.putCache(file_id, resp, "file_url")

        logger.debug("resp %s" % resp)
        return self.get_file_url(resp)

    def get_file_url(self, resp: GetDownloadUrlResponse) -> str:
        if resp.cdn_url is not None:
            return resp.cdn_url
        else:
            return resp.url
