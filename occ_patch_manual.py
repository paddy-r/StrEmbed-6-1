# -*- coding: utf-8 -*-
# """ HR 15/03/23 To modify OCC library to allow deep-copying of class instances """
import os
import inspect

from OCC.Core.Quantity import Quantity_Color
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TDF import TDF_Label


def create_new_methods_text(klass):
    klass_name = str(klass.__name__)
    old_text = klass_name + "(*args))"
    new_text = old_text + "\n\n" + \
        "        self.args = args\n\n" + \
        "    def __setstate__(self, state):\n" + \
        "        self.__init__(*state['args'])\n\n" + \
        "    def __getstate__(self):\n" + \
        "        if not hasattr(self, 'args'):\n" + \
        "            self.args = {}\n" + \
        "        return {'args': self.args}"

    return {old_text: new_text}


REPLACEMENTS_DEFAULT = {'split(".")[3]': 'split(".")[-1]'}
KLASSES_DEFAULT = [Quantity_Color, TopLoc_Location, TDF_Label]


def patch(replacements=REPLACEMENTS_DEFAULT,
          klasses=KLASSES_DEFAULT,
          outpath=None):

    for klass in klasses:

        full_path = inspect.getmodule(klass).__file__
        inpath, filename = os.path.split(full_path)
        if not outpath:
            outpath = inpath
        outpath_full = os.path.join(outpath, filename)
        print("Path to module file:", full_path)

        replacements.update(create_new_methods_text(klass))

        lines = []
        found = False
        with open(full_path) as infile:
            # Check if already patched, as mustn't do it more than once!
            file_string = infile.read()
            if "__getstate__" in file_string:
                print("File already patched; aborting")
            else:
                infile.seek(0) # Very important! Tracks back to beginning of file, as read() is an iterator
                for line in infile:
                    for src, target in replacements.items():
                        if src in line:
                            found = True
                            print("Found:", src)
                            line = line.replace(src, target)
                    lines.append(line)

        if found:
            print('Saving modified file in library for', klass, 'to', outpath_full)
            with open(outpath_full, 'w') as outfile:
                for line in lines:
                    outfile.write(line)
        else:
            print('No changes made to klass in library', klass)


if __name__ == "__main__":
    print("\nRunning 'patch' to allow deep-copying of PythonOCC SWIG objects")
    print("This allows StrEmbed assemblies to be duplicated and saved/loaded\n")
    patch()
