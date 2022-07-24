import io
import os
import tarfile
from datetime import datetime
from urllib.parse import parse_qs

from dav.file import AliyunDriveFile
from dav.response_stream import ResponseStream
from drive.model import FileItem


class AliyunDriveTarfile(AliyunDriveFile):

    def get_content_length(self):
        if tarinfo := self.get_tarinfo(self.file_item):
            return tarinfo.size
        return None

    def get_content(self):
        downurl = self.cache.get_downurl(self.file_item.file_id)
        if tarinfo := self.get_tarinfo(self.file_item):
            return ResponseStream(downurl, tarinfo.offset_data, tarinfo.size)

        return ResponseStream(downurl)

    def get_tarinfo(self, file_item: FileItem):
        file_id, url = file_item.file_id, file_item.url

        if tarinfo := self.cache.get(file_id, 'id_to_tarinfo'):
            return tarinfo

        downurl = ''
        expires = int(parse_qs(url).get('x-oss-expires', [0])[0])
        if expires > datetime.now().timestamp() + 60:
            downurl = url
        else:
            downurl = self.cache.get_downurl(file_id)

        tar_header = self.cache.drive.read_bytes(downurl, 512 * 3).content
        with io.BytesIO(tar_header) as f, tarfile.open(fileobj=f) as tar:
            tarinfo = tar.next()
            if tarinfo:
                self.cache.update(file_id, tarinfo, 'id_to_tarinfo')
            return tarinfo


encryption_mode = os.path.splitext(os.path.basename(__file__))[0]
file_class = AliyunDriveTarfile
