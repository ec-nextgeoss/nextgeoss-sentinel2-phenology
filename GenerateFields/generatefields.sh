#! /bin/bash


source ${ciop_job_include}

ciop-log "INFO" "Starting the generation of fields"


OUTPUT_DIR="`ciop-getparam output`"
WFS_URL="`ciop-getparam url`"	
WFS_LAYER="`ciop-getparam layer`"	
MINLAT="`ciop-getparam minLat`"	
MINLON="`ciop-getparam minLon`"	
MAXLAT="`ciop-getparam maxLat`"	
MAXLON="`ciop-getparam maxLon`"	
GROUPCOUNT="`ciop-getparam groupCount`"
SIZE="`ciop-getparam maxSize`"


outputDir="${TMPDIR}/${OUTPUT_DIR}"


ciop-log "INFO" "Creating output dir $outputDir"
mkdir -p ${outputDir}

ciop-log "INFO" "Field parameters: $WFS_URL - $WFS_LAYER - [$MINLAT, $MINLON, $MAXLAT, $MAXLON] - $GROUPCOUNT - $SIZE - $outputDir - $OUTPUT_DIR" 

docker run --rm  -v ${outputDir}:/${OUTPUT_DIR}                                    	      \
        vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.17    \
	python3 get_fields.py -url ${WFS_URL} -layer ${WFS_LAYER} -minLat ${MINLAT} -minLon ${MINLON} -maxLat ${MAXLAT} -maxLon ${MAXLON} -groups ${GROUPCOUNT} -maxSize ${SIZE} -output /$OUTPUT_DIR

ls -a ${outputDir}
ciop-publish ${outputDir}/*	
	
exit 0
