# Subject(観測対象)のインターフェース
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        # print("Subject", type(self))
        for observer in self._observers:
            # print("Observer", type(observer))
            observer.update(self)


# Observer(観測者)のインターフェース
class Observer:

    def update(self, subject):
        pass


class Mediator:
    def __init__(self):
        self.componets = []

    def add(self, componet):
        self.componets.append(componet)

    def send_event(self, event, sender):
        # print("Sender:", type(sender), "Event:", event)
        for componet in self.componets:
            if componet != sender:
                componet.receive_event(event)


class Component:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.mediator.add(self)

    def send_event(self, event=None):
        self.mediator.send_event(event, self)

    def receive_event(self, event):
        pass
