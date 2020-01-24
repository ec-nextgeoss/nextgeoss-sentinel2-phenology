#! /bin/bash


function publishFile() {
        dir=$1
        filename=$2

        ciop-log "INFO" "Checking if $1/$2 exists"

        if test -f "$1/$2"; then
                ciop-log "INFO" "$1/$2 exists"
                ciop-publish $1/$2
        else
                ciop-log "INFO" "$1/$2 does not exist"
        fi
}

function stageFile() {

	input=$1
	inputDir=$2
	ciop-log "INFO"  "New file that will be merged - ${input} and copied to ${inputDir}"
	geojson=$(echo $input | ciop-copy -U -o ${inputDir} -)
}


function main() {
	inputDir=$1
	outputDir=$2
	
	ciop-log "INFO" "Start merging files in ${inputDir} to ${outputDir}"
	
        docker run --rm -v ${TMPDIR}:/tmp                                            \
                vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.17           \
                python3 generate_phenology_output.py -i /tmp/input -o /tmp/output -f tif

        ciop-log "INFO" "Listing directory of ${outputDir}"
        ls -a ${outputDir}
	
	count=$(find . -type f | wc -l)
	
	if echo "$count" != "0"; then
		ciop-publish  ${outputDir}/* 
	fi

	
}


source ${ciop_job_include}

inputDir=${TMPDIR}/input
mkdir -p ${inputDir}

outputDir=${TMPDIR}/output
mkdir -p ${outputDir}



ciop-log "INFO" "Start merging of the output files"

while read input
do 
	stageFile ${input} ${inputDir}
done

main ${inputDir} ${outputDir}
