## Quick start guide for StrEmbed-6-1 as an executable (recommended; Windows only) or as a Python script

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6806818.svg)](https://doi.org/10.5281/zenodo.6806818)

Go to the latest release *via* the "Releases" tab, then either:

1. Download the ```StrEmbed_6_1``` zip file at the "Releases" tab. There is when unpacked, the folder contains the required Python modules and an executable. Run it by double-clicking; the ```StrEmbed-6-1``` app will run and does not require any other files - or Python - to be installed on your machine.
2. Download the source code file bundle (```.zip``` or ```.tar.gz``` format) and import into your Python environment. Instructions for setting up your environment and creating your own executable (not recommended) are given in the user manual.

___

# StrEmbed-6-1

Version 6-1 of Structure Embedding

Part of the Design Configuration Spaces (DCS) project hosted by the University of Leeds

Hugh Rice (HR/HPR), Tom Hazlehurst (TH) and Hau Hing Chau (HHC)

January 2020-August 2022

School of Mechanical Engineering  
University of Leeds  
LS2 9JT

All communication, including bug/issues reports, to: h.p.rice@leeds.ac.uk

___

<i> ```StrEmbed-6-1``` is a graphical user interface for visualisation and manipulation of part-whole relationships in assemblies of parts, and is written in Python. The user can read files in the [STEP format](https://en.wikipedia.org/wiki/ISO_10303-21), which is a common data exchange format containing both assembly information (i.e. part-whole information) and shape data. Functionality is based on [```StrEmbed-4```](https://github.com/hhchau/StrEmbed-4) (and earlier versions) by Hau Hing Chau, written in Perl.</i>  

<b>This research is supported by the UK Engineering and Physical Sciences Research Council (EPSRC) under grant number EP/S016406/1.</b>

___

## Full guide

There are several ways to run ```StrEmbed-6-1```, which are described below and in more detail in the user manual. The simplest is to download the latest release, which contains all the Python scripts and a standalone executable file. To run ```StrEmbed-6_1``` you can then do one of the following:

(1) Run as an executable. This does not require you to have Python or any IDE installed. Navigate to the "Releases" tab on the right of this page and download the zip file which, when unpacked, contains a folder with the executable. Once downloaded, double-click on the ```.exe``` file (Windows only) and the app will run. A console window will also open for debugging purposes. If you encounter any problems, please make a record of the output and contact the developers if you require help.

(2) Run as a Python script in your own environment. Two main scripts are required:

1. ```StrEmbed_6_1``` (main script)
2. ```step_parse_6_1``` (contains class for for file and graph operations)

The above incorporate code (specifically for the 3D viewer) from ```Python-OCC``` [here](https://github.com/tpaviot/pythonocc-core). ```StrEmbed-6_1``` has a large number of dependencies that must also be installed in your environment. Contact the developers of those packages if you encounter problems. Detailed instructions for setting up your Python environment using Anaconda or Miniconda are given in the user manual, which is part of this package.

Several STEP file examples are provided. The "Images" folder contains images necessary for building the application but not for running it.

```StrEmbed-6-1``` was developed in Spyder, an IDE for Python that is packaged with the Anaconda distribution, which can be downloaded [here](https://www.anaconda.com/distribution/).

```StrEmbed-6-1``` is published under the GNU General Purpose License version 3, which is given in the LICENSE document.
