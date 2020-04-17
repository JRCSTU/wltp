#!/bin/bash
#
# Utility to re-create `*.ipynb` files from the paired `*.py` "py:percent" files.
# (e.g. run it after clonining, to run `test_notebooks.py` with *papermill* lib)

# Convert "py:percent" files into Ipynbs
jupytext --sync Notebooks/*.py  Notebooks/Matlab/*.py
