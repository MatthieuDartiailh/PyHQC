PyHQC
=====

Python code that I write for the HQC lab (ENS-Paris)

How to install the HQC Viewer
-----------------------------

Assuming Anaconda 3.6 is already installed, one has to create first an environment with Python 2.7. Open a Conda bash shell and type `$ conda create -n py2 python=2`

Activate the environment: `$ activate py2`. After the installation, remember to check to be in the right environment, or activate it, every time you want to open the Viewer.

Go to https://github.com/MatthieuDartiailh/PyHQC , click on the green button `Clone or download` and download the .zip folder containing the Viewer

Move the .zip to a directory you like (here we call it ViewerDir) and extract it

To configure the needed packages, run the following lines

```shell
$ conda install configobj chaco watchdog -c ecpy
$ conda remove traitsui --force
$ pip install https://github.com/MatthieuDartiailh/persoTraitsui/tarball/master
```

At this point the Viewer can be opened: go to ViewerDir and run `$ python viewer_python.py`.
