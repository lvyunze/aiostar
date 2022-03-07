"""
Name : BaseTask
Author : blu
Time : 2022/3/7 08:19
Desc : 任务基类
"""


class BaseTask:

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def is_parallel(self):
        return False


if __name__ == '__main__':
    bt = BaseTask()
    print(bt.name)
