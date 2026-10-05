from abc import ABC, abstractmethod

class Observateur(ABC):

    @abstractmethod
    def actualiser(self, sujet) -> None:
        pass