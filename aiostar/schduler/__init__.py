"""
Name : schduler
Author : blu
Time : 2022/3/7 08:19
Desc : 调度器
"""
import queue

from aiostar.utils.LogManager import LogManager


class BaseSchduler():
    """
    调度器
    引擎通过调度器获取task 执行task的时候产生新的task会通过add方法加入到调度的队列中
    """

    def __init__(self):
        self.queue = queue.LifoQueue()
        self.logger = LogManager().get_log("schduler")

    def add(self, req):
        self.queue.put(req)

    def size(self):
        return self.queue.qsize()

    # def insert(self,idx, task):
    #     self.queue.

    def next_task(self):
        """
        返回下一个task，队列为空则返回None
        :return:
        """
        if self.queue.empty():
            return None
        task = self.queue.get()
        self.logger.info("size:{},pop_task:{}".format(self.size(), str(task)))
        return task


if __name__ == '__main__':
    b = BaseSchduler()
    b.next_task()
