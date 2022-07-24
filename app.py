import logging
import sys

from wsgidav.server.server_cli import _run_cheroot
from wsgidav.wsgidav_app import WsgiDAVApp

from dav.provider import AliyunDriveProvider

streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)

logging.getLogger('wsgidav').addHandler(streamHandler)

logger = logging.getLogger('aliyundrive-dav')
logger.addHandler(streamHandler)
logger.setLevel(logging.DEBUG)

config = {
    "host": "127.0.0.1",
    "port": 8080,
    # "http_authenticator": {},
    "simple_dc": {"user_mapping": {"*": True}},  # 匿名访问
    "server_args": {
        "numthreads": 10 # 线程数
    }
}


app = WsgiDAVApp(config)
app.add_provider("/", AliyunDriveProvider())


if __name__ == "__main__":
    logger.info(f'Serving on http://{config["host"]}:{config["port"]}')
    _run_cheroot(app, config, "cheroot")
