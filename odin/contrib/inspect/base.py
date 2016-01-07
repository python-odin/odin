from __future__ import print_function


class SummaryBase(object):
    """
    Base class for summaries
    """
    def __init__(self, out):
        self.out = out

    def print(self, *objects, sep=' ', end='\n'):
        print(*objects, sep=sep, end=end, file=self.out)

    def title(self, value, underline='='):
        self.print(value, underline * len(value), sep='\n')
