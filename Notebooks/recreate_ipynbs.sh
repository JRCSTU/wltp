#!/bin/bash
#
# Utility to re-create `*.ipynb` files from the paired `*.Rmd` files.
# (e.g. run it after clonining, to run `test_notebooks.py` with *papermill* lib)

# Convert Rmd files into Ipynbs
jupytext --to ipynb Notebooks/*.Rmd
# Fix "ipynb" later than Rmd" error on launch
rm Notebooks/*.Rmd
