###################
Contributing
###################

For submitting code, use ``UTF-8`` everywhere, unix-eol(``LF``) and set ``git --config core.autocrlf = input``.

The typical development procedure is like this:

1. Modify the sources in small, isolated and well-defined changes, i.e.
   adding a single feature, or fixing a specific bug.
2. Add test-cases "proving" your code.
3. Rerun all test-cases to ensure that you didn't break anything,
   and check their *coverage* remain above 80%:

    .. code-block:: console

        $ python setup.py nosetests --with-coverage --cover-package wltp.model,wltp.experiment --cover-min-percentage=80


    .. Tip:: You can enter just: ``python setup.py test_all`` instead of the above cmd-line
        since it has been *aliased* in the :file:`setup.cfg` file.
        Check this file for more example commands to use during development.


4. If you made a rather important modification, update also the :doc:`CHANGES` file and/or
   other documents (i.e. README.rst).  To see the rendered results of the documents,
   issue the following commands and read the result html at :file:`build/sphinx/html/index.html`:

    .. code-block:: console

        $ python setup.py build_sphinx                  # Builds html docs
        $ python setup.py build_sphinx -b doctest       # Checks if python-code embeded in comments runs ok.


5. If there are no problems, commit your changes with a descriptive message.

6. Repeat this cycle for other bugs/enhancements.
7. When you are finished, push the changes upstream to *github* and make a *merge_request*.
   You can check whether your merge-request indeed passed the tests by checking
   its build-status |build-status| on the integration-server's site (TravisCI).

    .. Hint:: Skim through the small IPython developer's documentantion on the matter:
        `The perfect pull request <https://github.com/ipython/ipython/wiki/Dev:-The-perfect-pull-request>`_


