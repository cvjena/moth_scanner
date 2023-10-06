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
