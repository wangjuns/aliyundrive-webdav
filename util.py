import os
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ADRIVE_REQ_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36 Edg/103.0.1264.44',
    'Referer': 'https://www.aliyundrive.com/',
    'Origin': 'https://www.aliyundrive.com',
}


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504),
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
