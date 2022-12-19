import logging
import os
import threading
from typing import Optional

from util import ROOT_DIR

logger = logging.getLogger('aliyundrive-dav')
cache_dir = os.path.join(ROOT_DIR, 'cache')
cache_path = os.path.join(cache_dir, 'data')

class Cache():
    
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self._load_cache()
        
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

    def read(self, key: str, group: Optional[str] = None):
        obj = self.cache.get(self._key(key, group))
        if obj is not None:
            logger.debug("cache hitted. %s" % (self._key(key, group)))
        else:
            logger.debug("cache missing. %s" % (self._key(key, group)))
        return obj

    def put(self, key: str, value, group: Optional[str] = None):
        self.cache.update({self._key(key, group): value})