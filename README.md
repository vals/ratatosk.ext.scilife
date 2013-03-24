## ratatosk.ext.scilife ##

`ratatosk.ext.scilife` is a `ratatosk` library extension. It contains
functions, configuration and customized scripts for running ratatosk
tasks at Science for Life Laboratory. Among other things, the module
is designed to work out of the box with raw data delivered from the
Science for Life Laboratory Genomics Core facility in Stockholm.

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

By default, samples sequenced at Science for Life Laboratory Genomics
Core Facility, Stockholm, are organized by directories *project name*,
*sample id*, and *flowcell*. Each flowcell, finally, contains the
sequence files (in gzipped fastq format) labelled with lane and
barcode sequence information. For obvious reasons, the test data in
[ngs.test.data](https://github.com/percyfal/ngs.test.data) has been
organized according to these principles. Running the command `tree` on
the project `J.Doe_00_01` yields

    |-- P001_101_index3
    |   |-- 120924_AC003CCCXX
    |   |   |-- P001_101_index3_TGACCA_L001_R1_001.fastq.gz
    |   |   |-- P001_101_index3_TGACCA_L001_R2_001.fastq.gz
    |   |   `-- SampleSheet.csv
    |   |-- 121015_BB002BBBXX
    |   |   |-- P001_101_index3_TGACCA_L001_R1_001.fastq.gz
    |   |   |-- P001_101_index3_TGACCA_L001_R2_001.fastq.gz
    |   |   `-- SampleSheet.csv
    |-- P001_102_index6
    |   `-- 120924_AC003CCCXX
    |       |-- P001_102_index6_ACAGTG_L002_R1_001.fastq.gz
    |       |-- P001_102_index6_ACAGTG_L002_R2_001.fastq.gz
    |       `-- SampleSheet.csv

Here, sample `P001_101_index3` has sequence data from flowcells
`120924_AC003CCCXX` and `121015_BB002BBBXX`, both run in lane 1
(`L001`) with barcode sequence `TGACCA`.

### Target generating functions ###

Some `ratatosk` tasks require helper functions that collect
information about samples and raw data. The `ratatosk.scilife` target
generating functions have been tailored to work with data organized as
described in the previous section. For instance, the function
`ratatosk.ext.scilife.sample.organize_sample_runs` collects and
organizes information about sample runs for task `MergeSamFiles` which
merges aligned sequences for a sample and places the output directly
in the sample folder. Similarly,
`ratatosk.ext.scilife.sample.target_generator` collects information
about project samples for use with best practice pipelines.

## Scripts ##

### ratatosk_run_scilife.py ###

The only difference between this script and the main `ratatosk` run
script is that `ratatosk_run_scilife.py` loads pipeline configuration
files located at `ratatosk.config.scilife`. These configuration files
use target generator functions specific to scilife data structure.

### ratatosk_submit_job.py ###

`ratatosk_submit_job.py` is a simple wrapper that uses the python
module `drmaa` for submitting ratatosk jobs to a cluster. 

