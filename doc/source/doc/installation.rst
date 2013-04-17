Installation
============

Pre-requisites
--------------

Install `ratatosk <https://github.com/percyfal/ratatosk>`_. To run the
full test suite, you also need to install the test data set
`ngs.test.data <https://github.com/percyfal/ngs.test.data.git>`_. The
test data set is necessary for testing and running the pipelines.

.. _installation:

Installation
------------

To install the development version of :mod:`ratatosk.ext.scilife`, do

.. code-block:: text
	
	git clone https://github.com/percyfal/ratatosk.ext.scilife
	python setup.py develop

Installation in UPPMAX
----------------------

pygraphviz
^^^^^^^^^^

Installing `Pygraphviz <http://networkx.lanl.gov/pygraphviz/>`_ with
``pip install pygraphviz`` often fails because the installer cannot
find the :program:`graphviz` library. One solution lies in modifying the
``setup.py`` that comes with the :mod:`pygrahviz` package. After a failed pip
install in virtual environment ``virtualenv`` (or whatever you called
it), you will typically find the failed build in
``~/.virtualenvs/virtualenv/build/pygraphviz``. In that directory,
modify the following section in  ``setup.py``:

.. code-block:: text

   # If the setup script couldn't find your graphviz installation you can
   # specify it here by uncommenting these lines or providing your own:
   # You must set both 'library_path' and 'include_path'

   # Linux, generic UNIX
   library_path='/usr/lib64/graphviz'
   include_path='/usr/include/graphviz'


Running the tests
-----------------

Cd to the luigi test directory (``tests``) and run

.. code-block:: text

	nosetests -v -s 

.. note:: Currently (20130417) many tests are failing but will be
   fixed shortly
	

Running example pipelines
^^^^^^^^^^^^^^^^^^^^^^^^^

For all examples, first cd to the :mod:`ratatosk.ext.scilife`
installation path. If you want to visualize the task graph (at
``localhost:8081``), make sure to start the server daemon
:program:`ratatoskd` in the background. The ``examples`` subdirectory
contains an example configuration file for project ``J.Doe_00_01``
that is used in the following examples.

.. note:: For the time being, you need to modify the paths to point to your ngs
   test data installation directory in the configuration file

.. note:: If a pipeline fails, make sure you have set the necessary
   environment variables ``GATK_HOME``, ``PICARD_HOME``, and
   ``SNPEFF_HOME``

To run the basic alignment pipeline, issue

.. code-block:: text

   ratatosk_run_scilife.py Align --indir /path/to/ngs.test.data/data/projects/J.Doe_00_01
     --outdir output_directory --custom-config examples/J.Doe_00_01 --workers 4

Analogously, to run the SeqCap pipeline, issue

.. code-block:: text

   ratatosk_run_scilife.py SeqCap --indir /path/to/ngs.test.data/data/projects/J.Doe_00_01
     --outdir output_directory --custom-config examples/J.Doe_00_01 --workers 4


Finally, to run the HaloPlex pipeline and run the summary, run

.. code-block:: text

   ratatosk_run_scilife.py HaloPlex --indir /path/to/ngs.test.data/data/projects/J.Doe_00_01
     --outdir output_directory --custom-config examples/J.Doe_00_01 --workers 4

   ratatosk_run_scilife.py HaloPlexSummary --indir /path/to/ngs.test.data/data/projects/J.Doe_00_01
     --outdir output_directory --custom-config examples/J.Doe_00_01 --workers 4

Testing issues
^^^^^^^^^^^^^^

 - During pipeline execution, a :program:`picard` tool
   (:program:`CreateSequenceDictionary`) is used to convert the
   reference
   ``/path/to/ngs.test.data/data/genomes/Hsapiens/hg19/seq/chr11.fa``
   to a dictionary file (``chr11.dict``). For some reason, this
   currently fails. Therefore you may need to run the command
   manually.
