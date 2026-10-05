# Used by Condor: run_job.sh <chunk_file> <job_id>
set -e
CHUNK=$1
JOBID=$2

# ROOT + Python source usage
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

export X509_USER_PROXY=$(pwd)/x509up # Uses grid certificate, expires 10/13

python3 muon_selection.py "$CHUNK" "out_${JOBID}.root" 
