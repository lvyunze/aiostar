"""
Name : ParallelTask
Author : blu
Time : 2022/3/7 08:19
Desc : 并行任务基类
"""
from aiostar.tasks import BaseTask


class ParallelTask(BaseTask):

    def __init__(self, fun, *args):
        self.fun = fun
        self.args = args
