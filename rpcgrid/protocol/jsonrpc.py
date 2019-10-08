import json

from rpcgrid.task import Task


class JsonRPC:
    def encode(self, task):
        # TODO: add naming params
        if task.method is not None:
            return json.dumps(
                {'id': task.id, 'method': task.method, 'params': task.params}
            )
        if task.error is not None:
            return json.dumps({'id': task.id, 'error': task.error})

        if task.result is not None:
            return json.dumps({'id': task.id, 'result': task.result})

    def decode(self, data):
        if data is None:
            return None
        if type(data) == list:
            datas = list(map(json.loads, data))
        else:
            datas = [json.loads(data)]
        tasks = []
        for data in datas:
            tsk = Task()
            tsk.id = data.get('id')
            tsk.method = data.get('method')
            tsk.params = data.get('params')
            tsk.result = data.get('result')
            tsk.error = data.get('error')
            tasks.append(tsk)
        return tasks