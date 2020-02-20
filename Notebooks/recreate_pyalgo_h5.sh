#!/bin/bash
#
# Run pyalgo on all AccDB cars
# needed for `CarsDB-compare` notebook.

my_dir=$(dirname "$0")

cd "$my_dir/.."
pytest -vsk test_taskforce_vehs --vehnums