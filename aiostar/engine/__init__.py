"""
Name : engine
Author : blu
Time : 2022/3/7 16:19
Desc : 引擎
"""
import asyncio
import inspect
import traceback
from typing import Awaitable, AsyncGenerator, Coroutine

from aiostar.downloader import BaseHttpDownloader
from aiostar.schduler import BaseSchduler
from aiostar.spiders import BaseSpider
from aiostar.tasks import BaseTask
from aiostar.tasks.Request import Request
from aiostar.tasks.Result import ResultTask
from aiostar.tasks.TaskHandler import TaskHandler
from aiostar.tasks.TaskLog import TaskLog
from aiostar.utils.LogManager import LogManager


class BaseEngine:
    """
    引擎
    """

    def __init__(self, setting: dict, scheduler: BaseSchduler,
                 app):
        """
        传入不同的实例来初始化引擎
        :param setting:
        :param scheduler:
        :param downloader:
        :param loop:
        """
        self.setting = setting
        self.work_num = setting.get("work_num", 1024)
        self.scheduler = scheduler
        self.app = app
        self.semaphore = asyncio.BoundedSemaphore(self.work_num)
        self.logger = LogManager().get_log("engine")

    def next_task(self):
        """
        从调度器中取出下一个任务
        :return:
        """
        return self.scheduler.next_task()

    def add_task(self, *args):
        """
        往调度器中添加一个task
        :param task:
        :return:s
        """
        return self.scheduler.add(args)

    async def _start(self):
        """
        不断的从调度器中取出task 去执行
        :return:
        """
        log_inv = 1000
        n = 0
        while True:
            n += 1
            if n >= log_inv:
                n = 0
                self.logger.info(f"semaphore_num:{self.semaphore._value}")
            if self.semaphore._value == 0:
                await asyncio.sleep(0.01)
                continue
            task = self.next_task()
            if not task:
                await asyncio.sleep(0.01)
                continue
            self.app.add_task(self._process_task_serially(*task))

    def start(self):
        self.app.add_task(self._start())

    async def gen_next_task_by_process_task(self, task, taskhandler, *args):
        async with self.semaphore:
            tasks = []
            if task is None:
                return tasks
            new_task = None
            # try:
            if isinstance(task, ResultTask):
                # 收集task
                new_task = task
            elif hasattr(task, '__iter__'):
                tasks = list(filter(lambda x: x, list(task)))
            elif isinstance(task, BaseTask):
                async for x in taskhandler._process(task, *args):
                    tasks.append(x)
            elif inspect.iscoroutinefunction(task):
                new_task = await task
            elif isinstance(task, AsyncGenerator):
                async for task in task:
                    tasks.append(task)
            elif isinstance(task, Coroutine):
                # Coroutine 的处理
                new_task = await task
            else:
                # print(tasks)
                raise NotImplementedError
            # except:
            #     traceback.print_exc()
            # finally:
            new_task and tasks.append(new_task)
            return tasks

    async def _process_task_parallelly(self, tasks, spider, *args):
        """
        并行执行 tasks中可并发的任务
        串行执行不可并发的任务
        可并行的任务 : task中is_parallel 为True | 生成器 (?: 生成器不可并发 会导致顺序问题)
        :param tasks:
        :param semaphore:
        :return:
        """

        async def run(async_tasks):
            return await asyncio.gather(*async_tasks)

        def is_paraller(tag_task):
            if isinstance(tag_task, BaseTask) and tag_task.is_parallel:
                return True
            return False

        all_result = []
        if not isinstance(tasks, list):
            tasks = [tasks]
        taskhandler = TaskHandler(spider)
        while tasks:
            task = tasks[0]
            if is_paraller(task):
                task_idx = [i for i, task in enumerate(tasks) if is_paraller(task)]
                results = await run(
                    [self.gen_next_task_by_process_task(tasks[i], taskhandler, *args)
                     for i in task_idx])
                all_tasks = 0
                for idx, result in zip(task_idx, results):
                    for t in result:
                        tasks.insert(idx + all_tasks, t)
                        all_tasks += 1
                    tasks.pop(idx + all_tasks)
                    all_tasks -= 1
            else:
                task = tasks.pop(0)
                if isinstance(task, ResultTask):
                    all_result.append(task)
                else:
                    results = await self.gen_next_task_by_process_task(task, taskhandler, *args)
                    tasks = results + tasks
        return all_result

    async def _process_task_serially(self, task):
        """
        单线程执行task
        直到执行完这个task 再释放信号
        :param tasks: 任务
        :param semaphore: 信号
        :return: 啥也不返回
        """
        async with self.semaphore:
            await task


if __name__ == '__main__':
    scheduler = BaseSchduler()
    downloader = BaseHttpDownloader()
    from aiostar.spiders.jiachunwang.S62 import Spider

    s62 = Spider()
    s62.set_logger_name("S62")
    engine = BaseEngine({}, scheduler, downloader)
    engine.start()
