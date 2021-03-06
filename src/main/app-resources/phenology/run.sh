#! /bin/bash




# Workflow step to calculate the cropphenology based on a given FeatureCollection. It returns the start and end of season for each of the given features



source ${ciop_job_include}



function main() {

	FEATURES="`ciop-getparam geojson`"
	SS="`ciop-getparam season_start_start`"
	SE="`ciop-getparam season_start_end`"
	MS="`ciop-getparam season_mid_start`"
	ME="`ciop-getparam season_mid_end`"
	ES="`ciop-getparam season_end_start`"
	EE="`ciop-getparam season_end_end`"
	ST="`ciop-getparam start_threshold`"
	ET="`ciop-getparam end_threshold`"

	INPUT_DIR="$TMPDIR/fields"
	INPUT_FILEPATH=$1
	INPUT_FILENAME=${INPUT_FILEPATH##*/}
	INPUT_BASENAME=${INPUT_FILENAME%.*}

	ciop-log "INFO" "Starting the calculation of crop phenology for $INPUT_FILENAME"

	ciop-log "INFO" "	Copy to local working dir"
	mkdir -p "$INPUT_DIR"
	GEOJSON=$(echo $INPUT_FILEPATH | ciop-copy -U -o $INPUT_DIR -)
	
	echo "TMPDIR INPUT"
	ls -al $TMPDIR/input

	ciop-log "INFO" "	Execute phenology calculation"
        source activate phenology
        cd ${_CIOP_APPLICATION_PATH}/phenology
	python calculate_phenology.py -sS $SS -sE $SE -mS $MS -mE $ME -eS $ES -eE $EE -sT $ST -eT $ET -i $TMPDIR/input/$INPUT_FILENAME -o $TMPDIR/shapes/$INPUT_BASENAME

	echo "TMPDIR OUTPUT:"
	ls -al "$TMPDIR/shapes"

}

ciop-log "INFO" "Creating output directory"
mkdir -p $TMPDIR/shapes
mkdir -p $TMPDIR/input
COUNT=1

while read input
do
	ciop-log "INFO" "Received input file: ${input}"
	DECODED_INPUT=$TMPDIR/input/fields_${COUNT}.json
	echo $input | base64 --decode >> $DECODED_INPUT
	ciop-log "INFO" "Input decoded to file ${DECODED_INPUT}"
	cat ${DECODED_INPUT}
	
	((COUNT+=1))
	main ${DECODED_INPUT}
done

ciop-log "INFO" "Publishing results"
ls -a $TMPDIR/shapes
count=$(find $TMPDIR/shapes -type f -name *.geojson | wc -l)
ciop-log "INFO" "Found $count results"
if [[ "$count" -ne 0 ]]; then
	ciop-publish $TMPDIR/shapes/*
else
  	ciop-log "INFO" "No results calculated"
fi
