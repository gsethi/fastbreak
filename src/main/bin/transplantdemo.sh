echo "workspace:" $1
echo "arguments:" $2

PYTHON=/local/bin/python2.6.5/python
JAVA=/tools/java/jdk1.6.0_11/bin/java
echo "using python version:" $PYTHON
echo "using java version:" $JAVA

if [[ $2 =~ "/addama/refgenome/hg18" ]]
then
REF_GEN="/local/addama/domains/public/scripts/transplantdemo/refgen18.out"
fi

sleep 5s

# TODO : Figure out the name of the file!
ZIP_FILE=../Archive.zip
echo "reference genome:" $REF_GEN
echo "source file zip:" $ZIP_FILE

$PYTHON /local/addama/domains/public/scripts/transplantdemo/importZip.py $ZIP_FILE $REF_GEN $1 /local/addama/domains/public/scripts/transplantdemo/pickleFiles

echo "storing patient model to workspace"
cp patients.json ../uploads/

echo "uploading patient gene score database"
cp patientgenescores.tsv ../uploads/

echo "uploading patient track database"
cp track.tsv ../uploads/

echo "setting up databases"
mkdir ../uploads/datasources/
cp /local/addama/domains/public/scripts/transplantdemo/track.json ../uploads/datasources/
cp /local/addama/domains/public/scripts/transplantdemo/patientgenescores.json ../uploads/datasources/

echo "completed"
