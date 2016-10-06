
class BaseField(object):
    # These track each time an instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self):
        self.creation_counter = BaseField.creation_counter
        BaseField.creation_counter += 1

    def __hash__(self):
        return self.creation_counter
