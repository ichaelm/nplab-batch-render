#!/bin/bash

# batch_render_stream.sh
# 
# usage:
# ./batch_render_stream.sh FILES_PER_THREAD MAX_NUM_THREADS [PROJECT_NAME] < STDIN
# 
# This script finds all the .mxs files in MXS_DIR, renders all of them with
# Maxwell Renderer using as many cluster jobs as it can without exceeding
# NUM_NODES, and outputs the resulting png images to OUTPUT_DIR with the same
# names, plus diagnostic output and error log files.

set -o nounset
set -o errexit

# parameters
NUM_MXS_FILES_PER_THREAD=$1
MAX_NUM_THREADS=$2
PROJNAME=${3-render} #optional

# constants
RESOLUTION="64x64"
SL=14

# global variables
THREAD_NUM=0
MY_TMP_DIR=$(mktemp -d tmp_batch_"$PROJNAME".XXXXXXXXXX)

# function gets temp file name for the given thread number
GetThreadPath () {
  RETVAL="${MY_TMP_DIR}/${PROJNAME}_thread_$1.tmp"
}

# function initializes temp file that lists MXS file paths
InitMXSFileList () {
  THREAD_NUM=$((THREAD_NUM+1))
  GetThreadPath ${THREAD_NUM}
  MXS_FILE_LIST_PATH=$RETVAL
  touch ${MXS_FILE_LIST_PATH}
  NUM_MXS_FILES_LISTED=0
}

# function adds the parameter to the MXS file path list
AddToMXSFileList () {
  echo $1 >> $MXS_FILE_LIST_PATH
  NUM_MXS_FILES_LISTED=$((NUM_MXS_FILES_LISTED+1))
}

# function starts a job to render the current list of files using Maxwell,
# clears the list and increments the thread number
StartRenderJob () {
  echo "Starting thread $THREAD_NUM with $NUM_MXS_FILES_LISTED files"
  qsub -N "${PROJNAME}_thread_${THREAD_NUM}"  -l walltime=23:00:00 \
    -l nodes=1:ppn=12,mem=10gb \
    -o ${MY_TMP_DIR}/${PROJNAME}_thread_${THREAD_NUM}_output.txt \
    -e ${MY_TMP_DIR}/${PROJNAME}_thread_${THREAD_NUM}_error.txt \
    -v MXS_FILE_LIST_PATH=${MXS_FILE_LIST_PATH},RESOLUTION=$RESOLUTION,SL=$SL \
    ./render_thread_stream.pbs
}

ReadyForThread () {
  BLOCKING_THREAD_NUM=$((THREAD_NUM-MAX_NUM_THREADS))
  if [ $BLOCKING_THREAD_NUM -gt 0 ]
  then
    GetThreadPath $BLOCKING_THREAD_NUM
    BLOCKING_THREAD_PATH=$RETVAL
    if [ -e $BLOCKING_THREAD_PATH ]
    then
      RETVAL=0
    else
      RETVAL=1
    fi
  else
    RETVAL=1
  fi
}

WaitUntilReady () {
  ReadyForThread
  while [ $RETVAL -eq 0 ]
  do
    sleep 1
    ReadyForThread
  done
}

# init log
echo "Running batch_render_stream.sh"
echo "Started $(date +%F\ %T)"

# log info
echo "PROJNAME = $PROJNAME"
echo "NUM_MXS_FILES_PER_THREAD = $NUM_MXS_FILES_PER_THREAD"

InitMXSFileList

# iterate over each mxs file
while read line
do
  MXS_PATH=$line

  AddToMXSFileList ${MXS_PATH}

  if [ $NUM_MXS_FILES_LISTED -eq $NUM_MXS_FILES_PER_THREAD ]
  then
    WaitUntilReady
    StartRenderJob
    InitMXSFileList
  fi
done

# final job for leftover files
if [ $NUM_MXS_FILES_LISTED -gt 0 ]
then
  WaitUntilReady
  StartRenderJob
else
  rm ${MXS_FILE_LIST_PATH}
fi

echo "Ended $(date +%F\ %T)"
