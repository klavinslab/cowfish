# Classes for interacting with models that appear in all Aquarium servers


class AquariumModel(object):
    def __init__(self, api):
        self.api = api
        return NotImplementedError

    def find(self, args):
        return NotImplementedError

    def create(self, args):
        return NotImplementedError

    def drop(self, args):
        return NotImplementedError

    def modify(self, args):
        return NotImplementedError


class Sample(AquariumModel):
    def __init__(self, args):
        return NotImplementedError


class Item(AquariumModel):
    def __init__(self, args):
        return NotImplementedError


class Task(AquariumModel):
    def __init__(self, args):
        return NotImplementedError
