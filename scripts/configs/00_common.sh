######################
#### Config files ####
######################

PYTHON_SETUP=${CONFIG_DIR}/01_python.sh
DATASET_OPTS=${CONFIG_DIR}/10_dataset.sh
MODEL_OPTS=${CONFIG_DIR}/20_model.sh

source ${PYTHON_SETUP}
source ${DATASET_OPTS}
source ${MODEL_OPTS}
