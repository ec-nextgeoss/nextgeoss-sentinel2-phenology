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

function main() {

	input=$1
	filename=${input##*/}
	basename=${filename%.*}	

	fieldsDir=${TMPDIR}/fields
	mkdir -p ${fieldsDir}

	outputDir=${TMPDIR}/shapes
	mkdir -p ${outputDir}

	geojson=$(echo $input | ciop-copy -U -o ${fieldsDir} -)


	ciop-log "INFO"  "Calculating the crop phenology params for ${filename}"

	docker run --rm  -v ${TMPDIR}:/tmp                                            \
	        vito-docker-private.artifactory.vgt.vito.be/nextgeoss-cropphenology:1.0.17           \
	        python3 calculate_phenology_params_json.py -sS "2018-04-02" -sE "2018-06-10" -mS "2018-06-10" -mE "2018-09-01" -eS "2018-09-01" -eE "2018-12-31" -sT 10.0 -eT 10.0 -i /tmp/fields/${filename} -o /tmp/shapes/${basename}

        ciop-log "INFO" "Listing directory of ${outputDir}"
	ls -a ${TMPDIR}/shapes
	count=$(find . -type f -name *.geojson | wc -l)
	
	if echo "$count" != "0"; then
		ciop-publish ${TMPDIR}/shapes/*
	fi
}



source ${ciop_job_include}

ciop-log "INFO" "Starting the calculation of crop phenology"

while read input
do 
	main ${input}
done


