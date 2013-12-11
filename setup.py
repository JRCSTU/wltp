# wltcg's setup.py
from distutils.core import setup
setup(
    name = "wltcg",
    packages = ["wltcg"],
    version = "0.0.0",
    description = "WLTC gear-shift calculator",
    author = "ankostis",
    author_email = "ankostis@gmail.com",
    url = "https://webgate.ec.europa.eu/CITnet/confluence/display/VECTO",
    download_url = "https://webgate.ec.europa.eu/CITnet/confluence/display/VECTO",
    keywords = ['wltc', 'cycles', 'emissions', 'simulation', 'vehicles', 'cars', 'nedc'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
WLTC gear-shift calculator
--------------------------

Implemented from the specs: https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179

This version requires Python 3 or later.
"""
)
