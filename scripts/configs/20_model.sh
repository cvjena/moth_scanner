BASE_MODEL_DIR=${BASE_MODEL_DIR:-${_home}/models/JENA_MOTHS}

CLASSIFIER=${CLASSIFIER:-${BASE_MODEL_DIR}/classifier/weights.npz}
DETECTOR=${DETECTOR:-${BASE_MODEL_DIR}/detector/weights.npz}


if [[ ! -f ${CLASSIFIER} ]]; then
	echo "Classifier model is not present: ${CLASSIFIER}!"
	error=1
fi


if [[ ! -f ${DETECTOR} ]]; then
	echo "Detector model is not present: ${DETECTOR}!"
	error=1
fi

OPTS="${OPTS} --classifier ${CLASSIFIER}"
OPTS="${OPTS} --detector ${DETECTOR}"
