#!/usr/bin/perl

use warnings;
use strict;
use utf8;
use List::Util qw(max);
use XML::Simple qw(:strict);
use Getopt::Long;
use File::Path qw(make_path);
use File::Copy;
use File::Basename;
use FindBin qw($RealBin);
use MIME::Lite;
use Proc::ProcessTable;
use Data::Dumper;
use List::MoreUtils qw(uniq);

my %opt;
GetOptions(\%opt, qw(run=s wd=s));

my ($date, $machineID, $runID, $flowCellID) = split /_/,$opt{'run'};
my $dataName = "20".substr($date,0,2).".".substr($date,2,2);
my $dataBase = "/HWPROJ2/lims/SJ/".$dataName;
my (%samHash,$sampleID,$laneID,$prod,$ind);
my $indSeq = "";
open PROD,"<","$opt{'wd'}/R1_Demultiplexed/production.txt" or die $!;
        while (<PROD>){
                if (/^C/){
                my @line = split /\s+/,$_;
                if ($line[-1] eq "Low"){
                        $prod = $line[-3];
                } else {
                        $prod = $line[-2];
                }
                ($sampleID,$laneID) = split '_L',$line[0];
                my ($Novo,$ext,$Ind1,$Ind2) = split '-',$sampleID;
                if (defined($Ind1) and defined($Ind2)){
                        $ind = $Ind1.";".$Ind2;
                }elsif (defined($Ind1) and !(defined($Ind2))){
                        $ind = $Ind1;
                }elsif (!(defined($Ind1)) and !(defined($Ind2))){
                        $ind = "";
                }
                open DATA,"<",$dataBase or die $!;
                        while (<DATA>){
                                my $line2 = $_;
                                if (!($ind eq "")){
#(index($line2,/^[$ind]$//) != -1))
                                        if ((index($line2,$opt{'run'}) != -1) and (substr($line2,0,1) eq $laneID) and (index($line2,$Novo."-".$ext) != -1) and ($line2 =~ /\s$ind\s/)){
                                                my @dataCont = split /\s+/,$line2;
                                                $indSeq = $dataCont[7];
                                        }
                                }elsif ($ind eq ""){
                                        if ((index($line2,$opt{'run'}) != -1) and (substr($line2,0,1) eq $laneID) and (index($line2,$Novo."-".$ext) != -1)){
                                                my @dataCont = split /\s+/,$line2;
                                                $indSeq = $dataCont[7];
                                        }
                                }
                        }
                close DATA;

                push(@{$samHash{$laneID}},"$sampleID\t$indSeq\t$prod");
                }
        }
close PROD;
my %lowCount;

for (keys %samHash){
        my $lane2 = $_;
        $lowCount{$lane2} = 0;
        open OUT,">","$opt{'wd'}/R1_Demultiplexed/L$lane2-output.txt" or die $!;
                print OUT "Lane $lane2. Low/no output:\n";
                my @samArr = @{$samHash{$lane2}};
                for (@samArr){
                        my ($samID,$indSeq2,$prod2) = split /\t/,$_;
                        if ($prod2 < 1.00){
                                print OUT "$samID\t$indSeq2\t$prod2\n";
                                $lowCount{$lane2}++;
                        }
                }
        close OUT;
}

for (keys %samHash){
        my $lane2 = $_;
        if ($lowCount{$lane2} > 20){
                $lowCount{$lane2} = $lowCount{$lane2} + 5;
        } else {
                $lowCount{$lane2} = 20;
        }
        system "sh $opt{'wd'}/R1_Demultiplexed/Top-Undetermined-R1-v1.5.sh $lane2 $lowCount{$lane2}";
        open TOP,"<","$opt{'wd'}/R1_Demultiplexed/TOP_$lane2" or die $!;
        open OUT,">>","$opt{'wd'}/R1_Demultiplexed/L$lane2-output.txt" or die $!;
        print OUT "\nUndetermined:\n";
        while (<TOP>){
                print OUT $_;
        }
        close TOP;
        close OUT;

}


for (keys %samHash){
        my $lane2 = $_;
        open OUT,">>","$opt{'wd'}/R1_Demultiplexed/L$lane2-output.txt" or die $!;
                print OUT "\nLane $lane2. Acceptable output:\n";
                my @samArr = @{$samHash{$lane2}};
                for (@samArr){
                        my ($samID,$indSeq2,$prod2) = split /\t/,$_;
                        if ($prod2 > 1.00){
                                print OUT "$samID\t$indSeq2\t$prod2\n";
                        }
                }
        close OUT;
}
