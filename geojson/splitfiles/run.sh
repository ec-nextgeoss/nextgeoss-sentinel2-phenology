#! /bin/bash




# Workflow step to calculate the cropphenology based on a given FeatureCollection. It returns the start and end of season for each of the given features



source ${ciop_job_include}

FEATURES="`ciop-getparam geojson`"
SIZE="`ciop-getparam max_size`"
OUTPUT_DIR="OUTPUT"

ciop-log "INFO" "Start splitting of input file to groups of size $SIZE"

ciop-log "INFO" "1.Create output directory"
mkdir -p "$TMPDIR/$OUTPUT_DIR/result"

ciop-log "INFO" "2. Split files"
docker run --rm  -v ${TMPDIR}:/tmp                                            \
                vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.18           \
                python3 split_files.py -geojson "$FEATURES" -size $SIZE -output /tmp/$OUTPUT_DIR/result

ciop-log "INFO" "3. Publishing results"
ls -a $TMPDIR/$OUTPUT_DIR/result
count=$(find $TMPDIR/$OUTPUT_DIR/result -type f -name *.geojson | wc -l)
ciop-log "INFO" "Found $count splitted geojson files"

if [[ "$count" -ne 0 ]]; then
	ciop-publish $TMPDIR/$OUTPUT_DIR/result/*
else
  	ciop-log "INFO" "No results calculated"
fi
