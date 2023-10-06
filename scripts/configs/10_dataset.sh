
# export DATA=${DATA:-$(realpath ${_home}/dataset_info.moths.yml)}

# if [[ ! -f $DATA ]]; then
# 	echo "DATA is not a file: ${DATA}"
# fi

# DATASET=${DATASET:-JENA_MOTHS}

N_JOBS=${N_JOBS:-3}

OPTS="${OPTS} --n_jobs ${N_JOBS}"
