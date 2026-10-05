# Used by Condor: run_job.sh <chunk_file> <job_id>
set -e
CHUNK=$1
JOBID=$2

### Grabbed from claude but unclear to me ###
# ROOT + Python usage?
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

# Proxy is transferred by Condor (x509userproxy); make sure xrootd sees it
export X509_USER_PROXY=$(pwd)/x509up
### ###

python3 muon_selection.py "$CHUNK" "out_${JOBID}.root" 
