"""
Name : run
Author : blu
Time : 2022/3/7 08:19
Desc : 启动文件
"""
from sanic import Sanic
import gc
import sys
import traceback
from sanic.response import json
import os
import psutil as pt
from sanic_cors import CORS
from aiostar.utils import spider_factory
from aiostar.engine import BaseEngine
from aiostar.schduler import BaseSchduler
from aiostar.utils.LogManager import LogManager

app = Sanic(__name__)
cors = CORS(app)


def print_name_memory():
    pids = pt.process_iter()
    for pid in pids:
        if pid.pid == os.getpid():
            print("Occupied memory:{:.2f}%".format(pid.memory_percent()))


@app.route("/fetch", methods=['GET', 'OPTIONS'])
async def spider_run(request):
    print_name_memory()
    spider_name = request.args.get("spider")
    msg = request.args.get("msg")
    xxl_id = request.args.get("id")
    # logger = LogManager().get_log("sanic")
    # logger.info("spider:{}\tmsg:{}".format(spider_name, msg))
    spider = spider_factory(spider_name, engine, xxl_id)

    await spider.run(msg)

    res = json({'data': spider.data, "status": 200, "code": 200, "message": "ok"})
    # del spider
    gc.collect()
    return res

scheduler = BaseSchduler()
# 新建engine实例
engine = BaseEngine({'work_num': 1024}, scheduler, app)
app_config = {"REQUEST_TIMEOUT": 600, "RESPONSE_TIMEOUT": 600}

app.update_config(app_config)
app.run(host="0.0.0.0", port=int(sys.argv[1]))