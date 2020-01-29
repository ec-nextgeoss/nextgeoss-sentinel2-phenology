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

	ciop-log "INFO" "	Execute phenology calculation"
	docker run --rm  -v ${TMPDIR}:/tmp                                            \
                vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.18           \
                python3 calculate_phenology_params_json.py -sS $SS -sE $SE -mS $MS -mE $ME -eS $ES -eE $EE -sT $ST -eT $ET -i /tmp/fields/$INPUT_FILENAME -o /tmp/shapes/$INPUT_BASENAME

	echo "TMPDIR LISTING:"
	ls -a "$TMPDIR/shapes"

}

ciop-log "INFO" "Creating output directory"
mkdir -p $TMPDIR/shapes


while read input
do
	ciop-log "INFO" "Received input file: ${input}"
	main ${input}
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
