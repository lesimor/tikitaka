from django.http import QueryDict
from tikitaka.utils.object import ObjectUtil


class BaseContext(object):
    def __init__(self, request):
        self._method = request.method
        self._path = request.META.get('PATH_INFO')
        self._headers = request.META
        self._parameters = self.extract_parameters(request)

    def get(self, key_path, default=None):
        """
        Get value from context
        :param key_path: path format ex) 'a.b.c'
        :param default: default value
        :return: any
        """
        value, found = ObjectUtil.get_from_path(self, key_path)
        if found is False:
            return default
        return value

    def get_from_parameters(self, key_path, default=None):
        value, found = ObjectUtil.get_from_path(self.parameters, key_path)
        if found is False:
            return default
        return value

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    @property
    def headers(self):
        return self._headers

    @property
    def parameters(self):
        return self._parameters

    @staticmethod
    def extract_parameters(request):
        parameters = QueryDict('', mutable=True)
        if request.GET:
            parameters.update(request.GET.copy())
        if request.POST:
            parameters.update(request.POST.copy())
        elif request.FILES:
            parameters.update(request.FILES.copy())
        elif request.body and (request.content_type == 'application/json' or request.body.lstrip().startswith(b'{')):
            try:
                parsed = json.loads(request.body)
            except ValueError:
                if request.content_type == 'application/json':
                    raise
            else:
                parameters.update(parsed)
        return parameters
