#!/bin/bash
#
# Run pyalgo on all AccDB cars
# needed for `CarsDB-compare` notebook.

papermill Notebooks/CarsDB-pyalgo.ipynb /tmp/CarsDB-pyalgo.ipynb \
	--cwd Notebooks \
    -p skip_h5_write False \
    -p force_h5_write True \
    -p del_h5_on_start False
