#################################
Installation & Build instructions
#################################


Quick-start
===========

Requires Python 3.3+.
Install it directly from the PyPI repository with the usual::

    $ pip3 install wltp

Or assuming you have download the sources::

    $ python setup.py install


More detailed installtion instructions from the ``tar.gz`` archive follow.

.. Seealso:: `WinPython <http://winpython.sourceforge.net/`


Installation
============

The first step is to expand the .tgz archive in a temporary directory (not directly in Python's site-packages).
It contains a distutils setup file "setup.py". OS-specific installation instructions follow.

GNU/Linux, BSDs, Unix, Mac OS X, etc.
-------------------------------------

* Open a shell.
* Go to the directory created by expanding the archive::

    $ cd <archive_directory_path>

* Install the package (you may need root permissions to complete this step)::

    $ su
    (enter admin password)
    # python setup.py install

If the python executable isn't on your path, you'll have to specify the complete path, such as /usr/local/bin/python.

To install for a specific Python version, use this version in the setup call, e.g.::

    $ python3.1 setup.py install

To install for different Python versions, repeat step 3 for every required version.
The last installed version will be used in the `shebang line <http://en.wikipedia.org/wiki/Shebang_%28Unix%29>`_
of the ``rst2*.py`` wrapper scripts.


Windows
-------
Install a *python-3* distribution for windows, ie:

* `WinPython <http://winpython.sourceforge.net/>`_
* `Enthought <https://www.enthought.com/products/epd/>`_


Just double-click ``install.py``. If this doesn't work, try the following:

* Open a DOS Box (Command Shell, MS-DOS Prompt, or whatever they're calling it these days).
* Go to the directory created by expanding the archive::

    $ cd <archive_directory_path>

* Install the package::

    $ python setup.py install

* To install for a specific python version, specify the Python executable for this version.

* To install for different Python versions, repeat step 3 for every required version.


Development:
------------
The WLTC-profiles for the various classes in the ``./util/data/cycles`` folder were generated from the tables
of the UN word-doc with the specs using the ``./util/csvcolumns8to2`` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.

Then use the :mod:`./util/buildwltcclass.py` to contruct the respective python-vars into the
:mod:`wltp/model.py` sources.


Test files generated and processed fromStven Heinz's db can be process
with scripts in ``/util`` folder.

.. TODO: running the test suite



