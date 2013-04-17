Helper scripts
==============

.. _ratatosk_run_scilife:

ratatosk_run_scilife.py
-----------------------

:program:`ratatosk_run_scilife.py` is a helper script that is shipped
with the ratatosk distribution. It collects the library wrapper tasks,
thus serving as an interface to small tasks, as well as pipeline
tasks. It is a modified version of :ref:`ratatosk_run.py ratatosk_run`
that loads configurations specific to Science for Life Laboratory.

Running :program:`ratatosk_run_scilife.py -h` shows the main options,
as well as the available tasks (abbreviated output for clarity):

.. code-block:: text


ratatosk_submit_job.py
----------------------

:program:`ratatosk_submit_job.py` is a script that submits jobs to a
cluster using the :mod:`drmaa` module, an implementation of the
`Distributed Resource Management Application API
<http://en.wikipedia.org/wiki/DRMAA>`_ specification. It is basically
a wrapper for :program:`ratatosk_run_scilife.py`, adding options for
drmaa.

.. code-block:: text
