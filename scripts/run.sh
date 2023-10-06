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

PYTHON="python"

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
