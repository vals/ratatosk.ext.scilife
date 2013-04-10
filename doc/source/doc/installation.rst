Installation
============

Pre-requisites
--------------

Install `ratatosk <https://github.com/percyfal/ratatosk>`_. To run the
full test suite, you also need to install the test data set
`ngs.test.data <https://github.com/percyfal/ngs.test.data.git>`_.

.. _installation:

Installation
------------

To install the development version of `ratatosk.ext.scilife`, do

.. code-block:: text
	
	git clone https://github.com/percyfal/ratatosk.ext.scilife
	python setup.py develop

Installation in UPPMAX
----------------------

pygraphviz
^^^^^^^^^^

Installing `Pygraphviz <http://networkx.lanl.gov/pygraphviz/>`_ with
```pip install pygraphviz``` often fails because the installer cannot
find the *graphviz* library. One solution lies in modifying the
`setup.py` that comes with the *pygrahviz* package. After a failed pip
install in virtual environment *virtualenv* (or whatever you called
it), you will typically find the failed build in
`~/.virtualenvs/virtualenv/build/pygraphviz`. In that directory,
modify the following section in `setup.py`:

.. code-block:: text

   # If the setup script couldn't find your graphviz installation you can
   # specify it here by uncommenting these lines or providing your own:
   # You must set both 'library_path' and 'include_path'

   # Linux, generic UNIX
   library_path='/usr/lib64/graphviz'
   include_path='/usr/include/graphviz'


Running the tests
-----------------

Cd to the luigi test directory (`tests`) and run

.. code-block:: text

	nosetests -v -s test_commands.py
	

