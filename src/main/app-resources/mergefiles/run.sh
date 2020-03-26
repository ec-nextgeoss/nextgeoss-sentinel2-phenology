#! /bin/bash


function stageFile() {

	INPUT=$1
	INPUT_DIR=$2
	ciop-log "INFO"  "New file that will be merged - $INPUT and copied to $INPUT_DIR"
	geojson=$(echo $INPUT | ciop-copy -U -o $INPUT_DIR -)
}


function main() {
	
	INPUT_DIR=$1
	OUTPUT_DIR=$2
	FORMAT="`ciop-getparam format`"
	
	ciop-log "INFO" "Start merging files in $INPUT_DIR to $OUTPUT_DIR"

	source activate phenology
	python ${_CIOP_APPLICATION_PATH}/mergefiles/merge.py -i $INPUT_DIR -o $OUTPUT_DIR -f $FORMAT -t $TMPDIR

        ciop-log "INFO" "Listing directory of $OUTPUT_DIR"
        ls -a $OUTPUT_DIR
	
	count=$(find $OUTPUT_DIR -type f | wc -l)
	ciop-log "INFO" "Found $count results"
	if [[ "$count" -ne 0 ]]; then
		ciop-publish -m $OUTPUT_DIR/* 
	fi

	
}


source ${ciop_job_include}

INPUT_DIR=${TMPDIR}/input
mkdir -p $INPUT_DIR

OUTPUT_DIR=${TMPDIR}/output
mkdir -p $OUTPUT_DIR



ciop-log "INFO" "Start merging of the output files"

while read input
do 
	stageFile ${input} $INPUT_DIR
done

main $INPUT_DIR $OUTPUT_DIR
