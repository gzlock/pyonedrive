# coding:utf-8
import os

from sanic import Sanic
from shortuuid import ShortUUID

from server import loop_task
from server.account import Account
from server.utils import sha256
from .admin import admin, admin_api
from .index import index


def server(obj, port: int, password: str):
    config = obj['config']
    cache = obj['cache']
    config['password'] = sha256(password)
    cache.set('config', config)
    print('服务器 最终设置', cache.get('config'))

    app = Sanic()

    Account.cache = cache
    Account.uuid = ShortUUID()

    @app.listener('before_server_start')
    async def setup_db(app, loop):
        app.cache = cache

    app.blueprint(index)
    app.blueprint(admin)
    app.blueprint(admin_api)

    # 静态文件资源
    res_path = os.path.join(os.path.dirname(__file__), 'res', 'resources')
    app.static('/resources/', res_path)

    loop_task.main(cache=cache)

    app.run(host='0.0.0.0', port=port)