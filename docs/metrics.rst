.. _metrics:

========================
Tests, Metrics & Reports
========================

In order to maintain the algorithm stable, a lot of effort has been put
to setup a series of test-case and metrics to check the sanity of the results
and to compare them with the Heinz-db tool or other datasets included in the project.
These tests can be found in the :file:`wltp/test/` folders.

Additionally, below are *auto-generated* representative diagrams with the purpose
to track the behavior and the evolution of this project.

You can reuse the plotting code here for building nice ipython-notebooks reports,
and (optionally) link them in the wiki of the project (see section above).
The actual code for generating diagrams for these metrics is in :class:`wltp.plots` and it is invoked
by scripts in the :file:`docs/pyplot/` folder.


Comparisons with Heinz-tool
===========================
This section compares the results of this tool to the Heinz's Access DB.

*Mean Engine-speed* vs *PMR*
----------------------------
First the mean engine-speed of vehicles are compared with access-db tool, grouped by PMRs:

.. plot:: pyplots/pmr_n_scatter.py


Both tools generate the same rough engine speeds.  There is though a trend for this project
to produce lower rpm's as the PMR of the vehicle increases.
But it is difficult to tell what each vehicle does isolated.

The same information is presented again but now each vehicle difference is drawn with an arrow:

.. plot:: pyplots/pmr_n_arrows.py

It can be seen now that this project's calculates lower engine-speeds for classes 1 & 3 but
the trend is reversed for class 2.

*Mean Engine-speed* vs *Gears*
------------------------------
Below the mean-engine-speeds are drawn against the mean gear used, grouped by classes and class-parts
(so that, for instance, a class3 vehicle corresponds to 3 points on the diagram):


.. plot:: pyplots/gears_n_arrows_class_1.py
.. plot:: pyplots/gears_n_arrows_class_2.py
.. plot:: pyplots/gears_n_arrows_class_3.py


Comparisons  with Older  versions
=================================
[TBD]


Discussion
----------
.. raw:: html

    <div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = 'wltp';
        var disqus_identifier = 'site.metrics';
        var disqus_title = 'wltp: Metrics';

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>

.. include:: ../README.rst
    :start-after: _begin-replacements: