#!/usr/bin/perl

use POSIX;
use File::Find;

######################################################################################################
######################################################################################################
if ($#ARGV+1 != 2){
   die "Run like this: perl age_and_prognosis.pl 20 70 #all patients between ages 20 and 70"
}

my ($ageMin, $ageMax) = @ARGV;

&identify_initial_diagnosis_date;
&identify_patient_status;

######################################################################################################
######################################################################################################

######################################################################################################
sub identify_patient_status
{
	%patient_status = ();
	%patient_stage = ();
	%three_yr_prognosis = ();
	$#status_contents = -1;
	#open (STAT, "< /titan/cancerregulome2/TCGA/clinical-data-repository/controlled.tcga-data.nci.nih.gov/tumor/ov/bcr/intgen.org/biotab/clin/clinical_patient_all_OV.txt") || die "cannot read patient status file: $!\n";
	open (STAT, "< /titan/cancerregulome3/TCGA/repositories/controlled.tcga-data.nci.nih.gov/tumor/ov/bcr/intgen.org/biotab/clin/clinical_patient_all_OV.txt") || die "cannot read patient status file: $!\n";
	@status_contents = <STAT>;
	close (STAT);
	
	foreach $line (@status_contents)
	{
		$age = "";
		
		#if ($line =~ /^TCGA-(\S+)\t.*?\t.*?\t.*?\t.*?\t.*?\t(\S+)\t.*?\t(\S+)\t(\S+)\t.*?\t.*?\t(\S+)\t.*?\t.*?\t.*?\t.*?\t.*?\t.*?\t.*?\t(\S+)\t/) # for public
		if ($line =~ /^TCGA-(\S+)\t.*?\t.*?\t.*?\t.*?\t.*?\t(\S+)\t.*?\t(\S+)\t(\S+)\t.*?\t.*?\t(\S+)\t.*?\t.*?\t.*?\t.*?\t.*?\t.*?\t.*?\t.*?\t(\S+)\t/) # for controlled
		{
			$patient = $1;
			$status = $2;
			$days_to_death = $3;
			$days_to_last_followup = $4;
			$age = $5;
			$stage = $6;
			#print "$patient\t$status\n";
			
			$patient_stage{$patient} = $stage;
			
			$years_to_last_followup = $days_to_last_followup/365.25;
			$years_to_death = $days_to_death/365.25;
			if (($years_to_last_followup >= 3) && ($status =~ /living/i))
			{
				$patient_status{$patient} = "1";
			}
			elsif ($status =~ /deceased/i)
			{
				$patient_status{$patient} = "-1";
			}
			if ($age >= $ageMin && $age < $ageMax){
			if (($years_to_last_followup >= 3) && ($status =~ /living/i))
			{
				$three_yr_prognosis{$patient} = "1";
				print "TCGA-$patient\t$age\t$years_to_last_followup\t1\n";
			}
			elsif (($years_to_death >= 3) && ($status =~ /deceased/i))
			{
				$three_yr_prognosis{$patient} = "1";
				print "TCGA-$patient\t$age\t$years_to_death\t0\n";
			}
			elsif (($status =~ /deceased/i) && ($years_to_death < 3))
			{
				$three_yr_prognosis{$patient} = "-1";
				print "TCGA-$patient\t$age\t$years_to_death\t-1\n";
			}
			}
		}
	}
	$#status_contents = -1;
}
######################################################################################################

######################################################################################################
sub identify_initial_diagnosis_date
{
	%date_of_initial_diagnosis = ();
	%year_of_initial_diagnosis = ();
	%inconsistent_diagnosis_date = ();

	find(\&xml, "/titan/cancerregulome2/TCGA/clinical\-data\-repository/controlled\.tcga\-data\.nci\.nih\.gov/tumor/ov/bcr/intgen\.org/bio/clin/");
	
	sub xml()
	{
		if (-f and /.xml?/)
		{
			$file = $_;
			$fullname=$File::Find::name;
			#intgen.org_full.TCGA-13-0886.xml
			if ($file =~ /TCGA-(\d{2}-\d{4})/)
			{
				$id = $1;
				$day=$month=$year="";
				open FILE, $file;
				@contents = <FILE>;
				close FILE;
				for $line (@contents)
				{
					#<INITIALPATHOLOGICDIAGNOSISDATE cde="58204" procurement_status="Completed" xsd_ver="1.9">2006-09-28 12:0000.0</INITIALPATHOLOGICDIAGNOSISDATE>
					if ($line =~ /\<INITIALPATHOLOGICDIAGNOSISDATE cde=\"\S+\" procurement_status=\"Completed\" xsd_ver=\"\S+\"\>(\d{4})-(\d{2})-(\d{2})\s*\S*\<\/INITIALPATHOLOGICDIAGNOSISDATE\>/)
					{
						($year, $month, $day) = ($1, $2, $3);
					}
					#<INITIALPATHOLOGICDIAGNOSISDAY cde="2896958" procurement_status="Completed" xsd_ver="1.12" tier="1">28</INITIALPATHOLOGICDIAGNOSISDAY>
					elsif ($line =~ /\<INITIALPATHOLOGICDIAGNOSISDAY cde="\S+" procurement_status=\"Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{2})\<\/INITIALPATHOLOGICDIAGNOSISDAY\>/)
					{
						$day = $1;
					}
					elsif ($line =~ /\<INITIALPATHOLOGICDIAGNOSISMONTH cde="\S+" procurement_status=\"Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{2})\<\/INITIALPATHOLOGICDIAGNOSISMONTH\>/)
					{
						$month = $1;
					}
					elsif ($line =~ /\<INITIALPATHOLOGICDIAGNOSISYEAR cde="\S+" procurement_status=\"Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{4})\<\/INITIALPATHOLOGICDIAGNOSISYEAR\>/)
					{
						$year = $1;
					}
					
					elsif ($line =~ /\<DAYOFINITIALPATHOLOGICDIAGNOSIS cde="\S+" procurement_status=\"TSS\: Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{2})\<\/DAYOFINITIALPATHOLOGICDIAGNOSIS\>/)
					{
						$day = $1;
					}
					elsif ($line =~ /\<MONTHOFINITIALPATHOLOGICDIAGNOSIS cde="\S+" procurement_status=\"TSS\: Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{2})\<\/MONTHOFINITIALPATHOLOGICDIAGNOSIS\>/)
					{
						$month = $1;
					}
					elsif ($line =~ /\<YEAROFINITIALPATHOLOGICDIAGNOSIS cde="\S+" procurement_status=\"TSS\: Completed\" xsd_ver=\"\S+\" tier=\"\S+\"\>(\d{4})\<\/YEAROFINITIALPATHOLOGICDIAGNOSIS\>/)
					{
						$year = $1;
					}
				}
				# print output for each file
				if (($day =~ /.+/) && ($month =~ /.+/) && ($year =~ /.+/))
				{
					if (not(defined($date_of_initial_diagnosis{$id})))
					{
						#print "$id\t$month\-$day\-$year\n";
						$date_of_initial_diagnosis{$id} = "$month\-$day\-$year";
						$year_of_initial_diagnosis{$id} = "$year";
					}
					#make sure it all matches
					elsif ((defined($date_of_initial_diagnosis{$id})) && ($date_of_initial_diagnosis{$id} !~ /^$month\-$day\-$year$/))
					{
						$inconsistent_diagnosis_date{$id} = 1;
						#print "error: date mismatch for patient $id - date of $month\-$day\-$year but expected $date_of_initial_diagnosis{$id}\n";
					}
				}
			}
		}
	}
}
######################################################################################################
