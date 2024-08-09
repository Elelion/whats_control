from abc import ABC, abstractmethod


# **

class AsicStatusInterface(ABC):
    @abstractmethod
    def get_asic_status(self):
        pass
