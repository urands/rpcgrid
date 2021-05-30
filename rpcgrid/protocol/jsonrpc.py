import json

from rpcgrid.task import AsyncTask


class JsonRPC:
    async def encode(self, task):
        # TODO: add naming params
        if task.error is not None:
            return json.dumps(
                {'jsonrpc': '2.0', 'id': task.id, 'error': task.error}
            )

        if task.result is not None:
            return json.dumps(
                {'jsonrpc': '2.0', 'id': task.id, 'result': task.result}
            )

        if task.method is not None:
            return json.dumps(
                {
                    'jsonrpc': '2.0',
                    'id': task.id,
                    'method': task.method,
                    'params': task.params,
                }
            )

    async def decode(self, data):
        if data is None:
            return None

        # TODO: add stream RPC data
        if len(data) > 2 and data[0] == '{' and data[-1] == '}':
            data = list(map(lambda x: '{' + x + '}', data[1:-1].split('}{')))

        if type(data) == list:
            try:
                datas = list(map(json.loads, data))
            except Exception as e:
                print(data)
                raise e
        else:
            datas = [json.loads(data)]
        tasks = []
        for data in datas:
            tsk = AsyncTask()
            tsk.id = data.get('id')
            tsk.method = data.get('method')
            tsk.params = data.get('params')
            tsk.result = data.get('result')
            tsk.error = data.get('error')
            tasks.append(tsk)
        return tasks
