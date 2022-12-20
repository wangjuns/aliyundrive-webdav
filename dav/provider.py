import logging
from typing import Optional

from drive.adpater import AliyunDriveAdapter
from drive.model import FileItem
from wsgidav import util
from wsgidav.dav_provider import DAVCollection, DAVProvider

from dav.file import AliyunDriveFile

logger = logging.getLogger('aliyundrive-dav')


class AliyunDriveProvider(DAVProvider):
    def __init__(self, refresh_token: str):
        super().__init__()
        self.aliyunDrive = AliyunDriveAdapter(refresh_token=refresh_token)

    def is_readonly(self):
        return True

    """
    path:
        root: /
        folder: /movie/苏里南.全6集/
        file: /movie/苏里南.全6集/01.NarcoSaints.2022.HD1080P.X264.AAC-YYDS.mp4
    """

    def get_resource_inst(self, path: str, environ: dict):
        try:
            return self.get_resource_inst0(path, environ)
        except Exception as inst:
            logger.error(inst.with_traceback())
            return None

    def get_resource_inst0(self, path: str, environ: dict):
        self._count_get_resource_inst += 1
        if path == '/':
            return AliyunDriveFolder(path, environ, self.aliyunDrive)

        item = self.aliyunDrive.get_item_by_path(path)
        if item is None:
            return None

        if item.type == 'folder':
            return AliyunDriveFolder(path, environ, self.aliyunDrive, item)

        return AliyunDriveFile(path, environ, self.aliyunDrive, item)


class AliyunDriveFolder(DAVCollection):

    def __init__(self, path, environ, cache: AliyunDriveAdapter, file_item: Optional[FileItem] = None):
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
                member_list.append(AliyunDriveFile(
                    path, self.environ, self.cache, item))

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
