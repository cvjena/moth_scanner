#!/usr/bin/env bash

BIG=0
GPU=${GPU:-0}

_home=${_home:-$(realpath $(dirname $0)/..)}
CONFIG_DIR=${_home}/scripts/configs

error=0

source configs/00_common.sh

OPTS="${OPTS} --gpu ${GPU}"


if [[ $error != 0 ]]; then
	exit $error
fi

export PYTHONPATH="${PYTHONPATH}:${_home}/../moth_detector"
export PYTHONPATH="${PYTHONPATH}:${_home}/../moth_classifier"

if [[ -z $DATA ]]; then
	echo "Please set DATA variable!"
	exit 2
fi

${PYTHON} ../src/main.py \
	${DATA} \
	${OPTS} \
	$@
