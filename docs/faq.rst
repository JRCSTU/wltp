===
FAQ
===

General
=======

Who is behind this?  How to contact the authors?
------------------------------------------------
The immediate involved persons is described in the :ref:`dev-team` section.
The author is a participating member in the :term:`GS Task-Force` on behalf of the EU Commission (JRC).

To contact the authors, use the DISQUS conversation, below, or create an issue.


What is the status of the project? Is it "official"?
----------------------------------------------------
It is a work-in-progress.  It is aimed to become "official".


What is the roadmap for this project?
-------------------------------------
- Short-term plans are described in the :ref:`todos-list` section of :doc:`CHANGES`.

- In the longer run, it is expected to incorporate more *WLTP* calculations and reference data so that
  this projects acts as repository for diagrams and technical reports on those algorithms.


Can I copy/extend it?  What is its License, in practical terms?
---------------------------------------------------------------
In a broad view, the core algorithm of the project is "copylefted" with
the *EUPL-1.1+ license*, and it includes files from other "non-copyleft" open source licenses like
-MIT MIT License* and *Apache License*, appropriately marked as such.  So in an nutshell, you can study it,
copy it, modify or extend it, and distrbute it, as long as you always distribute the sources of your changes.


Technical
=========
How do i "register" my *WinPython* installation?
------------------------------------------------
To register it, you need to perform 2 tasks: 

  and then :menuselection:`Options --> Register Distribution` .
- Ensure your installation is permanently added in your :envvar:`PATH`.
  For that you have to create or modify the registry string-key :samp:`[HKEY_CURRENT_USER\Environment:PATH]`.
  Use :program:`regedit.exe` and then **logoff** and **re-logon** to see the changes.


I followed the instructions but i still cannot install/run/do *X*.  What now?
-----------------------------------------------------------------------------
If you have no previous experience in python, setting up your environment and installing a new project
is a demanding, but manageable, task.  Here is a checklist of things that might go wrong:

- Did you send each command to the **appropriate shell/interpreter**?

  You should enter sample commands starting ``$`` into your *shell* (:program:`cmd` or :program:`bash`),
  and those starting with ``>>>`` into the *python-interpreter*
  (but don't include the previous symbols and/or the *output* of the commands).


- Is **python contained in your PATH** ?

  To check it, type `python` in your console/command-shell prompt and press :kbd:`[Enter]`.
  If nothing happens, you have to inspect :envvar:`PATH` and modify it accordingly to include your 
  python-installation. 
  
  - Under *Windows* type ``path`` in your command-shell prompt.
  - Under *Unix* type ``echo $PATH$`` in your console. 
    To change it, modify your "rc' files, ie: :file:`~/.bashrc` or :file:`~/.profile`.
  

- Is the correct **version of python** running?

  Certain commands such as :command:`pip` come in 2 different versions *python-2 & 3*
  (:command:`pip2` and :command:`pip3`, respectively).  Most programs report their version-infos
  with :option:`--version`.
  Use :option:`--help` if this does not work.


- Have you **upgraded/downgraded the project** into a more recent/older version?

  This project is still in development, so the names of data and functions often differ from version to version.
  Check the :doc:`CHANGES` for point that you have to be aware of when upgrading.


- Did you `search <https://github.com/ankostis/wltp/issues>`_ whether **a similar issue** has already been reported?

- Did you **ask google** for an answer??

- If the above suggestions still do not work, feel free to **open a new issue** and ask for help here.
  Write down your platform (Windows, OS X, Linux), your exact python distribution
  and version, and include the *print-out of the failed command along with its error-message.*

  This last step will improve the documentation and help others as well.


I do not have python / cannot install it.  Is it possible to try a *demo*?
--------------------------------------------------------------------------
Create an account into `Wakari <https://wakari.io/>`_ and post a Disqus-comment below
requesting JRC's shared IPython notebook.


Discussion
==========
.. raw:: html

    <div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = 'wltp';
        var disqus_identifier = 'site.faq';
        var disqus_title = 'wltp: Frequently Asked Questions';

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
