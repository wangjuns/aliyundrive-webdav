from drive.adpater import AliyunDriveAdapter
from drive.model import FileItem
from wsgidav import util
from wsgidav.dav_provider import DAVNonCollection

from dav.response_stream import ResponseStream


class AliyunDriveFile(DAVNonCollection):

    def __init__(self, path, environ, aliyunDrive: AliyunDriveAdapter, file_item: FileItem):
        super().__init__(path, environ)
        self.cache = aliyunDrive
        self.file_item = file_item

    def get_content_length(self):
        return self.file_item.size

    def get_content_type(self):
        return util.guess_mime_type(self.file_item.name)

    def get_etag(self):
        return None

    def support_etag(self):
        return False

    def support_ranges(self):
        return True

    def get_creation_date(self):
        return self.file_item.created_at.timestamp()

    def get_last_modified(self):
        return self.file_item.updated_at.timestamp()

    def get_content(self):
        downurl = self.cache.get_downurl(self.file_item.file_id)
        return ResponseStream(downurl)
