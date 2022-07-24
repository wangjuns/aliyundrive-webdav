import atexit
import logging
import os
import shelve
import threading
from datetime import datetime
from typing import List, Optional

from exts import get_ext_file_checks
from util import ROOT_DIR
from wsgidav import util

from drive.drive import AliyunDrive
from drive.model import FileItem

logger = logging.getLogger('aliyundrive-dav')
cache_dir = os.path.join(ROOT_DIR, 'cache')
cache_path = os.path.join(cache_dir, 'data')
ext_file_checks = get_ext_file_checks()


class Cache():

    def __init__(self) -> None:
        self.drive = AliyunDrive()
        self.lock = threading.Lock()
        self._load_cache()
        atexit.register(self.close)

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

    def compact(self):
        """
        释放缓存数据死空间，此操作会关闭缓存文件流并重新打开缓存文件流，需要加锁，与其他读写缓存操作互斥
        """
        with self.lock:
            data = {}
            for key in self.cache.keys():
                try:
                    data[key] = self.cache.get(key)
                except Exception as e:
                    logger.warning(f'Invalid key: {key}. Error: {e}')
            self.cache.close()
            for ext in ['.bak', '.dat', '.dir']:
                p = f'{cache_path}{ext}'
                if os.path.isfile(p):
                    os.remove(p)

            self._load_cache()
            self.cache.update(data)

    def _key(self, key: str, group: Optional[str] = None):
        return f'{group}.{key}' if group else key

    def get(self, key: str, group: Optional[str] = None):
        with self.lock:
            return self.cache.get(self._key(key, group))

    def update(self, key: str, value, group: Optional[str] = None):
        with self.lock:
            self.cache.update({self._key(key, group): value})

    def pop(self, key: str, group: Optional[str] = None):
        with self.lock:
            return self.cache.pop(self._key(key, group), None)

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

        if (
            (file_id := self.get(path, 'path_to_id')) and
            (file_list := self.get(file_id, 'id_to_list')) is not None
        ):
            return file_list

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

            if item.type == 'file':
                for check_func in ext_file_checks.values():
                    if new_item := check_func(item):
                        file_list.append(new_item)

        self.update(path, file_id, 'path_to_id')
        self.update(file_id, file_list, 'id_to_list')
        return file_list

    def get_downurl(self, file_id: str) -> str:
        """
        获取文件下载链接
        """
        downurl = self.get(file_id, 'id_to_downurl')
        if downurl and downurl.expiration.timestamp() > datetime.now().timestamp() + 3600:
            return downurl.url

        resp = self.drive.get_file_download_url(file_id)
        self.update(file_id, resp, 'id_to_downurl')
        return resp.url
