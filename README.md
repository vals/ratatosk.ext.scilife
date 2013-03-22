## ratatosk.ext.scilife ##

`ratatosk.ext.scilife` is a `ratatosk` library extension. It contains
functions, configuration and customized scripts for running ratatosk
tasks at Science for Life Laboratory. Among other things, the module
is designed to work out of the box with raw data delivered from the
Science for Life Laboratory Genomics Core facility. 

## Installing ##

### Pre-requisites ###

Install `ratatosk` by following the instructions at
[ratatosk](https://github.com/percyfal/ratatosk).

### Installation ###

To install the development version of `ratatosk.ext.scilife`, do
	
	git clone https://github.com/percyfal/ratatosk.ext.scilife
	python setup.py develop

## Implementation ##

### Data organization ###

## Scripts ##

### run_ratatosk_scilife.py ###

### submit_ratatosk_job.py ###

`submit_ratatosk_job.py` is a simple wrapper that uses the python
module `drmaa` for submitting ratatosk jobs to a cluster.

