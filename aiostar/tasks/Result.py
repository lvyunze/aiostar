"""
Name : Result
Author : blu
Time : 2022/3/7 08:19
Desc : 结果封装
"""
import json


class BaseResultTask:
    """
    result的基类
    """

    def __init__(self, obj, msg_task=None):
        self.data = obj
        self.skip_result_process = False
        self.ignore_process_confirm = False
        self.msg_task = msg_task

    @property
    def json(self):
        return self.to_json()

    def __str__(self):
        return str(self.data)

    __repr__ = __str__

    def to_json(self):
        if isinstance(self.data, str):
            return self.data
        return json.dumps(self.data, ensure_ascii=False)


class ResultTask(BaseResultTask):
    """
    一个 task的类型
    后面可能要添加不同的task
    然后插件根据task的类型作相应的处理
    """

    def __init__(
            self,
            result_handler,
            result_type='str',
            **kwargs
    ):
        super(ResultTask, self).__init__(kwargs)
        self.result_handler = result_handler
        if isinstance(self.result_handler, str):
            self.result_handler = [result_handler]
        self.result_type = result_type
        for k in kwargs:
            setattr(self, k, kwargs[k])


if __name__ == '__main__':
    x = ResultTask(
        result_handler="kuaixun",
        content=""
    )
