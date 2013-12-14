==========================
WLTC gear-shift calculator
==========================

WLTCG calculates the gear-shifts of light-duty-vehicles (cars) for the WLTC testing-cycle.

It accepts as input the car-specifications and a selection of a WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.  To install it, do the usual::

	python setup.py install


Typical usage would look like this::

	import wltcg

	specs = {
		vehicle : { },
		options : { },
	}

	results = wltcg(specs)

	print(results)

		{...}


For Python 3.3 or later.



Build
-----

The WLTC-profiles for the various classes were generated from the tables of UN word-doc with the specs
using the ``util/csvcolumns8to2`` script, requiring an intermediate manual step.



History
-------

Implemented from the UN's specs (document also included in the docs):
  https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179

By ankostis@gmail.com, Dec-2013, JRC, (c) AGPLv3 or later



Thanks also to
--------------

* Giorgos Fontaras for physics, policy and admin support.
* Steven Heinz for his test-data.
