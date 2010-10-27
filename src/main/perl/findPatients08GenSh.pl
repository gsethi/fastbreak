#!/usr/bin/perl

use POSIX;
use File::Find;
#use strict;

######################################################################################################
######################################################################################################
# outputs sh commands for pass 1 findtrans.py to run on linux servers
#ie nice ../bin/samtools-0.1.7_x86_64-linux/samtools view  /titan/cancerregulome1/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1/tranche_07/TCGA-25-1328-10A-01W-0492-08.sorted.bam | nice /tools/bin/python findtrans.py TCGA-25-1328-10A-01W-0492-08-medium-0630 medium 1000 50 1000 1 0 1 0 > TCGA-25-1328-10A-01W-0492-08-medium-0630.log

my ($patientSetFile, $cancer, $shLabel, $class, $cr_drive, $minSize, $maxSize, $tileWindow, $transRange1, $transRange2, $reportOD, $generateFastQ, $reportMM, $doRG) = @ARGV;

die usage() unless ($patientSetFile and $shLabel);
sub usage {
	print "Usage perl findPatients08GenSh.pl tcgaPatients.tsv cancertype batch_label class_label cancerregulomeDrive minSize maxSize tileWindow transRange1 transRange2 reportOrientationAndDistance generateFastQ reportMappingMetrics ie\nUse 0 for false and 1 for true\n perl findPatients08GenSh.pl ./tcga_ov.tsv gbm 0708batch Silver cancerregulome2 10 500 1000 50 1000 1 0 1 1\n";
}
$shLabel_ext = "../sh/" . $shLabel . ".sh";

open FILE, ">$shLabel_ext" or die $!;

my $patientShBuff = "";
my $patientFileSizeBuff = "";
my $patientFilenameBuff = "";
my $statusGrp = "";
my %fcmd_hash = ();
my %fsize_hash = ();
my %patient_paired_hash = ();
######################################################################################################
######################################################################################################
&find_patient_files_for_tranx;

######################################################################################################
sub find_patient_files_for_tranx
{
        open (STAT, "< $patientSetFile") || die "cannot read patient status file: $!\n";
        @status_contents = <STAT>;
        close (STAT);
	print "Patient-Sample\tAge\tPrognosis\tStatus\tBamFileSize\tRGCount\n";
	#print "Patient file set between " . $minSize . " " . $maxSize . " gbs in $cr_drive status (Good) 1 = still living,(Medium) 0 = deceased after 3 years,(Poor) -1 = deceased within 3 years\n";
        foreach $line (@status_contents)
        {
                $age = "";
		@tokens = split(/\t/, $line);
		$patientName = @tokens[0];
		$status = int(@tokens[3]);
		$age = @tokens[1];
		$statusLabel = "good";
		if ($status == -1){
			$statusLabel = "poor";
		}elsif ($status == 0){
			$statusLabel = "medium";
		}
		$statusGrp = $statusLabel . $class;
		if ($doRG eq "1"){
			$statusGrp = $statusGrp . "RG";
		}
		find (\&myfind, "/titan/" . $cr_drive . "/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/" . $cancer);
		#ov/phs000178v1/p1");		
		sub myfind(){
			if (-f and (/^$patientName.*?-08.sorted.bam$/)){
				$filename = $File::Find::dir . "/" . $_;
				print("found $filename\n");
				@splitted = split("/", $filename);
				$filen = $splitted[$splitted-1];
				$patientFullname = substr($filen, 0, -11); 
				$patientLabel = $patientFullname . "-" . $statusLabel . "_" . $age .  "-" . $shLabel;
				$logLabel = $patientLabel . ".log"; 
				$filesize_mb = int((-s $filename) / (1024 * 1024 * 1000)); #format_bytes(-s $filename);
				$myFileInfo = $patientFileBuff . $filename . " " . $filesize_mb;
				#print("found $filename GBs $filesize_mb\n");
				$rgCount = 0;
				if ($filesize_mb > $minSize and $filesize_mb < $maxSize){
					#$fsize_hash{ $patientName } = $filesize_mb/1000;
					my $fhn = $filename . ".header";
					if (-e $fhn) {					
						open HFILE, "<$fhn" or die $!;
						$rgCount = 0;
						while (my $hline = <HFILE>) {
							@tks = split(/\t/, $hline);
					     		$tk0 = @tks[0];	
					     			if ($tk0 eq "\@RG"){
									$rgCount = $rgCount + 1;
									$patientFilenameBuff = $patientFilenameBuff . $filename . "\n";
					     			}	
						}
					}
					if (exists $fcmd_hash{$patientName}) {
						my $filesize_1 = $fsize_hash{ $patientName };
						my $filesize_diff = abs($filesize_1 - ($filesize_mb));
						my $patientLine2 = $patientFullname. "\t" . @tokens[1]. "\t" . @tokens[2]. "\t" . $statusLabel. "\t" . $filesize_mb. "\t" . $rgCount . "\n";
						my $patientLine1 = $patient_paired_hash{ $patientName };
						print "$patientLine1$patientLine2";
						$patientFileSizeBuff = $patientFileSizeBuff . "file size differences for patient " . $patientName . " " . $filesize_diff . "\n";	
	                                       $sampleShCmd = $fcmd_hash{ $patientName };	 
					       $patientShBuff = $patientShBuff . $sampleShCmd . "echo 'begin $patientFullname'\ndate\nnice /titan/cancerregulome2/bin/samtools-0.1.7_x86_64-linux/samtools view -h  $filename | nice /tools/bin/python /titan/cancerregulome2/synthetic_cancer/python/findtrans.py $cancer $patientLabel $statusGrp $tileWindow $transRange1 $transRange2 $reportOD $generateFastQ $reportMM $doRG > $logLabel\n";
					}else{
						$fsize_hash{ $patientName } = $filesize_mb;
						$fcmd_hash{ $patientName } = "echo 'begin $patientFullname'\ndate\nnice /titan/cancerregulome2/bin/samtools-0.1.7_x86_64-linux/samtools view  -h $filename | nice /tools/bin/python /titan/cancerregulome2/synthetic_cancer/python/findtrans.py $cancer $patientLabel $statusGrp $tileWindow $transRange1 $transRange2 $reportOD $generateFastQ $reportMM $doRG > $logLabel\n";
						#if (($patientFullName =~ /01[A,B,C]/) || ($patientFullName =~ /10[A,B,C]/)){
							$patient_paired_hash{$patientName} = $patientFullname. "\t" . @tokens[1]. "\t" . @tokens[2]. "\t" . $statusLabel. "\t" . $filesize_mb. "\t" . $rgCount . "\n"; 
						#}
					}
				}
			}
		}
	}

}

=pod
foreach $key (sort (keys(%grades))) {
   print "\t\t$key \t\t$grades{$key}\n";
}
=cut
for my $key ( sort (keys %fsize_hash) ) {
           my $value = $fsize_hash{$key};
           #print "$key\t$value mbs\n";
}

print "\nPatients with multiple sample types, sh cmds\n $patientShBuff";
$patientShBuff = $patientShBuff . "echo 'pass 1 completed'\ndate\n";
print FILE $patientShBuff;
close FILE;

print $patientFileSizeBuff;
#print $patientFilenameBuff;
