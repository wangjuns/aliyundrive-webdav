import logging
from typing import Optional

import requests

from util import ADRIVE_REQ_HEADERS

logger = logging.getLogger('aliyundrive-dav')


class ResponseStream():

    def __init__(self, url: str, offset: int = 0, size: Optional[int] = None) -> None:
        self.url = url
        self.offset = offset
        self.size = size
        self.range_start = 0
        self.range_end: Optional[int] = None
        self.resp = None

        if offset > 0:
            assert size is not None

    @property
    def range_header(self):
        start = self.range_start
        end = self.range_end
        if self.offset > 0:
            start = start + self.offset
            if end is None:
                end = self.offset + self.size - 1
            else:
                end = end + self.offset

        header = {'Range': f'bytes={start}-{end or ""}'}
        logger.debug(f'Actual range header: {header}')
        return header

    def close(self):
        if self.resp:
            self.resp.close()
            self.resp = None
            logger.debug(f'ResponseStream.closed.')

    def read(self, block_size: int):
        if self.resp is None:
            logger.debug(
                f'ResponseStream new request. Range: bytes={self.range_start}-{self.range_end or ""}')
            self.resp = requests.get(
                self.url,
                headers={**ADRIVE_REQ_HEADERS, **self.range_header},
                stream=True
            )
        return self.resp.raw.read(block_size)

    def seek(self, offset):
        self.range_start = offset
        self.close()
