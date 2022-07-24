import logging
from typing import Optional

from drive.cache import Cache
from drive.model import FileItem
from exts import get_ext_file_classes
from wsgidav import util
from wsgidav.dav_provider import DAVCollection, DAVProvider

from dav.file import AliyunDriveFile

logger = logging.getLogger('aliyundrive-dav')
ext_file_classes = get_ext_file_classes()


class AliyunDriveProvider(DAVProvider):
    def __init__(self):
        super().__init__()
        self.cache = Cache()

    def is_readonly(self):
        return True

    def get_resource_inst(self, path, environ):
        self._count_get_resource_inst += 1
        if path == '/':
            return AliyunDriveFolder(path, environ, self.cache)

        item = self.cache.get_item_by_path(path)
        if item is None:
            return None

        if item.type == 'folder':
            return AliyunDriveFolder(path, environ, self.cache, item)

        file_class = ext_file_classes.get(
            item.encryption_mode, AliyunDriveFile)
        return file_class(path, environ, self.cache, item)


class AliyunDriveFolder(DAVCollection):

    def __init__(self, path, environ, cache: Cache, file_item: Optional[FileItem] = None):
        super().__init__(path, environ)
        self.cache = cache
        self.file_item = file_item
        self.file_list = []

    @property
    def file_id(self):
        if self.file_item:
            return self.file_item.file_id
        return 'root'

    def get_member_list(self):
        logger.debug(f'Get member list. path: {self.path}')
        file_list = self.cache.get_file_list_by_path(
            self.path.rstrip('/') + '/')

        member_list = []
        for item in file_list:
            path = util.join_uri(self.path, item.name)
            if item.type == 'folder':
                member_list.append(
                    AliyunDriveFolder(path, self.environ, self.cache, item))
            else:
                file_class = ext_file_classes.get(
                    item.encryption_mode, AliyunDriveFile)
                member_list.append(
                    file_class(path, self.environ, self.cache, item))

        return member_list

    def get_member_names(self):
        return []

    def get_creation_date(self):
        if self.file_item:
            return self.file_item.created_at.timestamp()
        return None

    def get_last_modified(self):
        if self.file_item:
            return self.file_item.updated_at.timestamp()
        return None

    def support_modified(self):
        return self.file_item is not None
