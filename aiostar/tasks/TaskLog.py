"""
Name : TaskHandler
Author : blu
Time : 2022/3/7 08:19
Desc : 任务日志封装
"""
from aiostar.tasks import BaseTask


class TaskLog(BaseTask):
    """
    日志类
    需要什么添加什么
    """

    def __init__(self, s):
        self.msg = s
