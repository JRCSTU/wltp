#!/bin/bash
#
# Utility to re-create `*.ipynb` files from the paired `*.py` "hydrogen" files.
# (e.g. run it after clonining, to run `test_notebooks.py` with *papermill* lib)

# Convert "python-hydrogen" files into Ipynbs
jupytext --sync Notebooks/*.py
