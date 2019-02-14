#!/bin/csh
#SBATCH  --job-name=python
#SBATCH  --nodes=1
#SBATCH  --output=python_scr.%j
#SBATCH --output=out.slurm
#SBATCH --error=err.slurm
#SBATCH -t 00:30:00
#SBATCH -A uq_climate
#SBATCH -p short


module load python/2.7.8
python -u ne30_fc5_cloud_test_new_env.py
