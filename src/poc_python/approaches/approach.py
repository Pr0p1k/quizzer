
from abc import ABC, abstractmethod

class Approach(ABC):
    @abstractmethod
    def get_langgraph_graph(self):
        pass
