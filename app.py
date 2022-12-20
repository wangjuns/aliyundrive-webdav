import logging
import sys
import argparse

from wsgidav.server.server_cli import _run_cheroot
from wsgidav.wsgidav_app import WsgiDAVApp
from logging.handlers import RotatingFileHandler
from dav.provider import AliyunDriveProvider


parser = argparse.ArgumentParser("webdav")
parser.add_argument("--log", help='set log level', default='INFO')
parser.add_argument("-t", help='set refresh token', default=None)
args = parser.parse_args()

streamHandler = RotatingFileHandler("logs/webdav_app.log", maxBytes=1024*1024*50, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)

# logging.getLogger('wsgidav').addHandler(streamHandler)

logger = logging.getLogger('aliyundrive-dav')
logger.addHandler(streamHandler)
logger.setLevel(logging._nameToLevel[args.log])

config = {
    "host": "0.0.0.0",
    "port": 8080,
    # "http_authenticator": {},
    "simple_dc": {"user_mapping": {"*": True}},  # 匿名访问
    "server_args": {
        "numthreads": 10  # 线程数
    }
}

refresh_token = args.t
assert refresh_token is not None

logger.debug(f"using refresh token {refresh_token}")

app = WsgiDAVApp(config)
app.add_provider("/", AliyunDriveProvider(refresh_token))


if __name__ == "__main__":
    logger.info(f'Serving on http://{config["host"]}:{config["port"]}')
    _run_cheroot(app, config, "cheroot")
