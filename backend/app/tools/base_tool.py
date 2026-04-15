from abc import ABC, abstractmethod

class BaseTool(ABC):

    name: str

    @abstractmethod
    async def run(self, input_data: str):
        pass
