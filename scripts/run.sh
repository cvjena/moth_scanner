#!/usr/bin/env bash
error=0

GPU=${GPU:-0}
OPTS="${OPTS} --gpu ${GPU}"

_home=${_home:-$(realpath $(dirname $0)/..)}


if [[ -z $DATA ]]; then
	echo "Please set DATA variable!"
	error=1
fi

######################
### Python Config
######################
source ${_conda:-${HOME}/.miniconda3}/etc/profile.d/conda.sh
conda activate ${CONDA_ENV:-moth_scanner}

if [[ $GDB == "1" ]]; then
	echo "GDB debugging enabled!"

	PYTHON="gdb -ex run --args python"

elif [[ $N_MPI -gt 1 ]]; then
	echo "MPI execution enabled!"

	HOSTFILE=${HOSTFILE:-hosts.conf}

	# create hosts file with localhost only
	if [[ ! -f ${HOSTFILE} ]]; then
		echo "localhost slots=${N_MPI}" > ${HOSTFILE}
	fi
	ENV="-x PATH -x OMP_NUM_THREADS -x MONGODB_USER_NAME -x MONGODB_PASSWORD -x MONGODB_DB_NAME"
	PYTHON="orterun -n ${N_MPI} --hostfile ${HOSTFILE} --oversubscribe --bind-to socket ${ENV} python"

elif [[ $PROFILE == "1" ]]; then
	echo "Python profiler enabled!"

	PYTHON="python -m cProfile -o profile"

else
	PYTHON="python"
fi

if [[ ! -z $DRY_RUN ]]; then
	echo "Dry run enabled!"
	PYTHON="echo ${PYTHON}"
fi

######################
### Model Config
######################

BASE_MODEL_DIR=${BASE_MODEL_DIR:-${_home}/models/JENA_MOTHS}

CLASSIFIER=${CLASSIFIER:-${BASE_MODEL_DIR}/classifier/weights.npz}
DETECTOR=${DETECTOR:-${BASE_MODEL_DIR}/detector/weights.npz}


if [[ ! -f ${CLASSIFIER} ]]; then
	echo "Classifier model is not present: ${CLASSIFIER}!"
	error=2
fi


if [[ ! -f ${DETECTOR} ]]; then
	echo "Detector model is not present: ${DETECTOR}!"
	error=3
fi

OPTS="${OPTS} --classifier ${CLASSIFIER}"
OPTS="${OPTS} --detector ${DETECTOR}"


######################
### Adding submodules
######################

export PYTHONPATH="${PYTHONPATH}:${_home}/src/modules/moth_detector"
export PYTHONPATH="${PYTHONPATH}:${_home}/src/modules/moth_classifier"

######################
### Final checks
######################

if [[ $error != 0 ]]; then
	exit $error
fi

${PYTHON} ${_home}/src/main.py \
	${DATA} \
	${OPTS} \
	$@
