# HR 31/01/23 To monkey-patch PythonOCC classes to allow them to be deep-copied
# Followed logic from here: https://stackoverflow.com/questions/19545982/monkey-patching-a-class-in-another-module-in-python
# Avoids modifying package scripts, but must be executed every time StrEmbed is run
# Also see (not used so far): https://stackoverflow.com/questions/2789460/python-add-to-a-function-dynamically
# ...and another example: https://stackoverflow.com/questions/33868886/how-can-one-attach-a-decorator-to-a-function-after-the-fact-in-python


# Basic klass for testing
class a:
    def __init__(self, *k, **kw):
        print('Before modification')


# Append __init__
def make_newinit(klass):
    oldinit = klass.__init__
    def newinit(self, *k, **kw):
        oldinit(self, *k, **kw)
        self.args = k
        print('After modification')
    klass.__init__ = newinit


def __setstate__(self, state):
    self.__init__(*state['args'])


def __getstate__(self):
    if not hasattr(self, 'args'):
        self.args = {}
    return {'args': self.args}


#KLASS_LIST_DEFAULT = [OCC.Core.Quantity.Quantity_Color, OCC.Core.TopLoc.TopLoc_Location, OCC.Core.TDF.TDF_Label]
KLASS_LIST_DEFAULT = [a, a]


# Main body of function
def patch(klass_list = KLASS_LIST_DEFAULT):

    print('Trying to modify OCC classes to allow deep-copying...')

    print('Klasses to be modified:')
    for klass in klass_list:
        print('-', klass.__name__)

    for klass in klass_list:

        # 1. Add self.args to __init___
        print('Trying to add self.args to __init__ of klass:', klass.__name__)

        testinstance = klass()
        if hasattr(testinstance, "args"):
            print('Klass instantiation already creates "args"; aborting')
        else:
            print('Modifying __init__ to include self.args in klass', klass.__name__)
            make_newinit(klass)
            # oldinit = klass.__init__
            # def newinit(self, *k, **kw):
            #     oldinit(self, *k, **kw)
            #     self.args = k
            #     print('After modification')
            # klass.__init__ = newinit

        # 2. Add __setstate__ and __getstate__ methods
        print('Trying to add __setstate__ and __getstate__ methods to klass:', klass.__name__)

        if hasattr(klass, "__setstate__"):
            print('Klass already has __setstate__; aborting')
        else:
            print('Adding __setstate__')
            klass.__setstate__ = __setstate__
            print(klass.__setstate__)

        if hasattr(klass, "__getstate__"):
            print('Klass already has __getstate__; aborting')
        else:
            print('Adding __getstate__')
            klass.__getstate__ = __getstate__

if __name__ == "__main__":
    patch()