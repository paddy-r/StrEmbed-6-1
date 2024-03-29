## Quick start guide for StrEmbed-6-1 as an executable (recommended; Windows only) or as a Python script

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6806818.svg)](https://doi.org/10.5281/zenodo.6806818)

You can download ```StrEmbed``` as an executable or as source code to run in your Python environment. A quick start guide for both options is given below.

1. (Recommended) Download the ```StrEmbed.exe``` executable file from the "Releases" page (see link on right-hand side of this page). Double-click the file and the ```StrEmbed``` app will run; it does not require Python or anything else to be installed on your machine.
2. Download the source code file bundle (```.zip``` or ```.tar.gz``` format) from the "Code" tab at the top of this page, then import the necessary files into your Python environment. Detailed instructions for setting up your environment and creating your own executable (not recommended) are given in the user manual and here. For this option and the one below, you must also install ```PartFind```, a dependency of ```StrEmbed```, with this command: ```pip install git+https://github.com/thazlehurst/partfind@strembed_legacy```
3. Alternatively, clone the repository using ```git```. Use the following command: ```git clone https://github.com/paddy-r/StrEmbed-6-1```, the install into your environment with ```pip install -v -e .```.

___

# StrEmbed-6-1

Version 6-1 of Structure Embedding

Part of the Design Configuration Spaces (DCS) project hosted by the University of Leeds

Hugh Rice (HR/HPR), Tom Hazlehurst (TH) and Hau Hing Chau (HHC)

January 2020-February 2023

School of Geography and School of Mechanical Engineering  
University of Leeds  
LS2 9JT

All communication, including bug/issues reports, to: h.p.rice@leeds.ac.uk

___

<i> ```StrEmbed``` is a graphical user interface for visualisation and manipulation of part-whole relationships in assemblies of parts, and is written in Python. The user can read files in the [STEP format](https://en.wikipedia.org/wiki/ISO_10303-21), which is a common data exchange format containing both assembly information (i.e. part-whole information) and shape data. Functionality is based on [```StrEmbed-4```](https://github.com/hhchau/StrEmbed-4) (and earlier versions) by Hau Hing Chau, written in Perl.</i>  

<b>This research is supported by the UK Engineering and Physical Sciences Research Council (EPSRC) under grant number EP/S016406/1.</b>

___

## Full guide

There are several ways to run ```StrEmbed```, which are described below and in more detail in the user manual. The simplest is to download the latest release, which contains all the Python scripts and an executable file. To run ```StrEmbed``` you can then do one of the following:

(1) Run as an executable. This does not require you to have Python or any IDE installed. Navigate to the "Releases" page using the link on the right of this page and download the ```StrEmbed.exe```file; double-click it (Windows only) and the app will run. A console window will also open for debugging purposes. If you encounter any problems, please make a record of the output and contact the developers if you require help. You can capture the output in a text file with the following command (Windows only):

```
StrEmbed.exe > log.txt & log.txt
```

(2) Run as a Python script in your own environment. Two main scripts can be used:

1. ```StrEmbed``` (main script, runs the app)
2. ```step_parse``` (contains all non-app functionality for file and graph operations)

The above incorporate code (specifically for the 3D viewer) from ```Python-OCC``` [here](https://github.com/tpaviot/pythonocc-core). ```StrEmbed``` has a large number of dependencies that must also be installed in your environment. Contact the developers of those packages if you encounter problems. Detailed instructions for setting up your Python environment using Anaconda or Miniconda are given in the user manual, which is part of this package. The instructions must be followed closely.

Several STEP file examples are provided. The "Images" folder contains images necessary for building the application but not for running it.

```StrEmbed``` is published under the GNU General Purpose License version 3, which is given in the LICENSE document.

## Contact and issue reporting

Please either raise an issue here at Github or contact me directly.

*Contact:* Hugh Rice, h.p.rice@leeds.ac.uk

## How to cite this repository

- Copy or click the Zenodo link above, which has a corresponding DOI attached, and construct your own citation that contains it.
- Depending on your style, your citation should look something like this: Rice HP (2022), *StrEmbed-6-1: A software prototype for product configuration management*, Github code repository, DOI: <latest DOI, see above>.
- If you're unsure, please contact me.
