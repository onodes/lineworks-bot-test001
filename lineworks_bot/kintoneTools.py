import pykintone
from pykintone import model
from abc import ABCMeta, abstractmethod

class GourmetMapLayout(model.kintoneModel):
    def __init__(self):
        super(GourmetMapLayout, self).__init__()
        self.account_id = ""
        self.filename = ""



class Kintone(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, subdomain, app_id, token):
        pass
    
    @abstractmethod
    def create(self, record):
        pass



class GrourmetMap(Kintone):
    def __init__(self, subdomain, app_id, token):
        self.application = pykintone.app(subdomain, app_id, token)

    def create(self, record):
        res = self.application.create(record)
        return res