#!/usr/bin/perl -w

#
# Script to sync matefiles for PE alignment using Illumina data
# Agilent Technologies
#
# Modified 20130428 by Per Unneberg. 
# 
# The first implementation hashed
# the entire input sequence files, causing the program to crash when
# working on large input files. The new "-a" option uses the first
# implementation whereas the default now is to only hash the ids and
# re-read the sequence files when outputting the synced reads
#

use strict;
use warnings;
use Getopt::Long;
use FileHandle;
use IO::Uncompress::Gunzip;

my($in1,$in2,$out1,$out2,$hash_all);
GetOptions("i=s" => \$in1,"j=s" => \$in2,"o=s" => \$out1,"p=s" => \$out2, "a" => \$hash_all);
usage() if(!$in1 || !$in2 || !$out1 || !$out2);


# read file
my %h;
my @idlist;

# hash both mates
hashFile($in1,"m1");
hashFile($in2,"m2");

if (not $hash_all) {
  # define filehandles for reading input once again
  if ($in1 =~ /.gz$/) {
    open(INMATE1, "gunzip -c $in1 |") || die "Can't open file";
  } else {
    open(INMATE1, $in1) || die "Can't open file";
  }
  if ($in2 =~ /.gz$/) {
    open(INMATE2, "gunzip -c $in2 |") || die "Can't open file";
  } else {
    open(INMATE2, $in2) || die "Can't open file";
  }
}

# define filehandles for printing mates
if ($out1 =~ /.gz$/) {
  open(MATE1, "| gzip -c > $out1") || die "Can't open file";
} else {
  open(MATE1, "> $out1") or die $!;
}
if ($out2 =~ /.gz$/) {
  open(MATE2, "| gzip -c > $out2") || die "Can't open file";
} else {
  open(MATE2, "> $out2") or die $!;
}

if ($hash_all) {
  # loop over hash and print to each output
  for my $id (keys %h) {
    if($h{$id}{'m1'}{'seq'} && $h{$id}{'m2'}{'seq'}) {
      print MATE1 printRead($h{$id}{'m1'});
      print MATE2 printRead($h{$id}{'m2'});
    }
  }
} else {
  # loop over idlist and print to each output. Requires reading input
  # sequence files again and forwarding to correct id. @idlist must therefore be ordered
  my ($s1, $s2);
  for my $id (@idlist) {
    if($h{$id}{'m1'} && $h{$id}{'m2'}) {
      $s1 = nextSeq(*INMATE1, $id);
      $s2 = nextSeq(*INMATE2, $id);
      print MATE1 $s1;
      print MATE2 $s2;
    }
  }
  close(INMATE1);
  close(INMATE2);
}

close(MATE1);
close(MATE2);

# Get next wanted sequence from input
sub nextSeq {
  my ($fh, $wantid) = @_;
  my ($id, $rid, $seq, $qual);
  while (1) {
    $id = <$fh>;
    chomp $id;
    ($rid,undef) = $id =~ m/^(.*?)[\s\/][12].*?$/;
    $seq = <$fh>; chomp($seq);
    <$fh>; # Jump one row...
    $qual = <$fh>; chomp($qual);
    if ($rid eq $wantid) {
      last;
    }
  }
  return "$id\n$seq\n+\n$qual\n";
}

# print the fastq read
sub printRead {
  my %r=%{$_[0]};
  return "$r{'id'}\n$r{'seq'}\n+\n$r{'qual'}\n";
}


# set id to hash
sub hashFile {
  my($file,$mate)=@_;
  my($id, $rid, $seq, $qual);
  if ($file =~ /.gz$/) {
    open(FH, "gunzip -c $file |") || die "Can't open file";
  } else {
    open(FH, $file) || die "Can't open file";
  }
  while(<FH>) {
    chomp;
    $id = $_;
    ($rid,undef) = $id =~ m/^(.*?)[\s\/][12].*?$/;
    $seq = <FH>; chomp($seq);
      <FH>; # Jump one row...
    $qual = <FH>; chomp($qual);
    if ($hash_all) {
      if(length($seq) != 0) {
	$h{$rid}{$mate}{'id'}=$id;
	$h{$rid}{$mate}{'seq'}=$seq;
	$h{$rid}{$mate}{'qual'}=$qual;
      }
    } else {
      if ($mate eq "m1") {
	push @idlist, $rid;
      }
      if(length($seq) != 0) {
	$h{$rid}{$mate}{'id'}=$id;
      }
    }
  }
  close(FH);
}


# usage information
sub usage {
  print "\nUsage: $0\n
-a     Hash entire reads (default: false)
-i     Input for mate1
-j     Input for mate2
-o     Output for mate1
-p     Output for mate2\n\n";
  exit(1);
}
