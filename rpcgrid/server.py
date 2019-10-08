import threading


class Methods:
    _methods = {}

    def add(self, name, func):
        if not callable(func):
            raise AttributeError(f"{name}:{func} not callable")
        self._methods[name] = func

    def call(self, method, *args, **kwargs):
        if method in self._methods:
            return self._methods[method](*args, **kwargs)
        raise Exception(f'Method {method} not allowed')


class GlobalMethods(Methods):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Server:
    _provider = None

    def __init__(self, provider):
        self._provider = provider
        self._provider.create(self.method_call)

    @property
    def provider(self):
        return self._provider

    def run(self):
        while threading.main_thread().is_alive():
            task = self._provider.recv()
            if task is not None:
                response = self.method_call(task)
                self.provider.send(response)

    def method_call(self, task):
        methods = GlobalMethods()
        try:
            task.result = methods.call(task.method, *task.params)
        except Exception as e:
            task.error = str(e)
        finally:
            task.method = None
        return task
