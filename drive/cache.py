import logging
import os
import shelve
import threading
from typing import List

from wsgidav import util

from drive.drive import AliyunDrive
from drive.model import FileItem
from util import ROOT_DIR

logger = logging.getLogger('aliyundrive-dav')
cache_dir = os.path.join(ROOT_DIR, 'cache')
cache_path = os.path.join(cache_dir, 'data')

class Cache():

    def __init__(self) -> None:
        self.drive = AliyunDrive()
        self.lock = threading.Lock()
        # self._load_cache()
        # atexit.register(self.close)

    def _load_cache(self):
        """
        打开缓存文件流
        """
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        self.cache = shelve.open(cache_path)

    def close(self):
        """
        关闭缓存文件流
        """
        self.cache.close()


    def get_item_by_path(self, path: str):
        """
        根据路径获取file_item
        """
        assert path.startswith('/') and path != '/'
        uri_parent = util.get_uri_parent(path)
        uri_name = util.get_uri_name(path)
        for item in self.get_file_list_by_path(uri_parent):
            if item.name == uri_name:
                return item

        return None

    def get_file_list_by_path(self, path: str) -> List[FileItem]:
        """
        根据路径获取文件列表
        """
        assert path.startswith('/') and path.endswith('/')

        uri_parent = util.get_uri_parent(path)
        if uri_parent is None:
            return self._get_file_list('/', 'root')

        uri_name = util.get_uri_name(path)
        for item in self.get_file_list_by_path(uri_parent):
            if item.name == uri_name:
                return self._get_file_list(path, item.file_id)

        return []

    def _get_file_list(self, path: str, file_id: str):
        file_list = []

        for item in self.drive.list_all_files(file_id):
            file_list.append(item)

        return file_list

    def get_downurl(self, file_id: str) -> str:
        """
        获取文件下载链接
        """

        resp = self.drive.get_file_download_url(file_id)
        return resp.url
