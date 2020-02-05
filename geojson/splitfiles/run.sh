#! /bin/bash




# Workflow step to calculate the cropphenology based on a given FeatureCollection. It returns the start and end of season for each of the given features



source ${ciop_job_include}

MODE="`ciop-getparam mode`"
INPUT_DATA="`ciop-getparam geojson`"
SIZE="`ciop-getparam max_size`"
OUTPUT_DIR="OUTPUT"

ciop-log "INFO" "Start splitting of input file to groups of size $SIZE"

ciop-log "INFO" "1.Create output directory"
mkdir -p "$TMPDIR/$OUTPUT_DIR/result"


ciop-log "INFO" "2. Checking mode $MODE"

if [[ "$MODE" -eq "shapefile" ]]; then
	ciop-log "INFO" "  Reading shapefile from input"
	while read input
	do
	        TMP_PATH=$(ciop-copy -o $TMPDIR "${input}")
		if [[ $TMP_PATH == *".shp" ]]; then
			ciop-log "INFO" "    Found shapefile $TMP_PATH"
			INPUT_DATA="/tmp/${TMP_PATH##*/}"
		fi
	done
fi

ciop-log "INFO" "3. Split files"

ciop-log "INFO" "  Splitting input file $INPUT_DATA with mode $MODE"
ls -al $TMPDIR

ciop-log "INFO" "  Calling -input "$INPUT_DATA" -size $SIZE -output /tmp/$OUTPUT_DIR/result -mode $MODE"

docker run --rm  -v ${TMPDIR}:/tmp -v /application:/application                                            \
                vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.19           \
                python3 split_files.py -input "$INPUT_DATA" -size $SIZE -output /tmp/$OUTPUT_DIR/result -mode $MODE

ciop-log "INFO" "4. Publishing results"
ls -a $TMPDIR/$OUTPUT_DIR/result
count=$(find $TMPDIR/$OUTPUT_DIR/result -type f -name *.geojson | wc -l)
ciop-log "INFO" "  Found $count splitted geojson files"

if [[ "$count" -ne 0 ]]; then
	ciop-publish $TMPDIR/$OUTPUT_DIR/result/*
else
  	ciop-log "INFO" "No results calculated"
fi
