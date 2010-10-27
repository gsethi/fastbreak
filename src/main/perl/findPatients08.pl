#!/usr/bin/perl

use POSIX;
use File::Find;

######################################################################################################
######################################################################################################


######################################################################################################
######################################################################################################
&identify_patient_status;

######################################################################################################
sub identify_patient_status
{
        open (STAT, "< /Volumes/jlin/tcga_ov_patients.txt") || die "cannot read patient status file: $!\n";
        @status_contents = <STAT>;
        close (STAT);
	print "Patient\tAge\tPrognosis\tStatus\n";
	print "CancerRegulome1, * means that patient has 08 data, status 1 = still living, 0 = deceased after 3 years, -1 = deceased within 3 years\n";
        foreach $line (@status_contents)
        {
                $age = "";
                #print "$line";
		@tokens = split(/\t/, $line);
		$patientName = @tokens[0];
		#print "$patientName\n";
		find (\&myfind, "/Volumes/CancerRegulome1/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1");		
		sub myfind(){
			if (-f and /^$patientName.*?-08.sorted.bam$/){
				$filename = $_;
				#if ($filename /$patientName?/)
				#{
				#	print "$tokens[0]*\t$tokens[1]\t$tokens[2]\t$tokens[3]\n";
				#}
				print "*$line";			
			}
		}
	}

	print "\nCancerRegulome2, * means that patient has 08 data, status 1 = still living, 0 = deceased after 3 years, -1 = deceased within 3 years\n";
        foreach $line (@status_contents)
        {
                $age = "";
                #print "$line";
                @tokens = split(/\t/, $line);
                $patientName = @tokens[0];
                #print "$patientName\n";
                find (\&myfind, "/Volumes/CancerRegulome2/TCGA/clinical-data-repository/dbgap.ncbi.nlm.nih.gov/ov/phs000178v1/p1");
                sub myfind(){
                        if (-f and /^$patientName.*?-08.sorted.bam$/){
                                $filename = $_;
                                #if ($filename /$patientName?/)
                                #{
                                #       print "$tokens[0]*\t$tokens[1]\t$tokens[2]\t$tokens[3]\n";
                                #}
                                print "*$line";
                        }
                }
        }

}
