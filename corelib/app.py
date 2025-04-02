from abc import ABC, abstractmethod

class App(ABC):

    @abstractmethod
    def start(self):
        pass

