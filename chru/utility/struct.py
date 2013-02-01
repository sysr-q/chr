# -*- coding: utf-8 -*-
class struct:
    """ This class is just a simple way to convert a
        dictionary to an object, for easier interaction.

        Instead of ``o['this']``, you can do ``o.this``;
        Isn't it great?!
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return str(self.__dict__)