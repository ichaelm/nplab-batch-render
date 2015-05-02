#!/bin/bash

# batch_render.sh
# 
# usage:
# ./batch_render.sh MXS_DIR OUTPUT_DIR [PROJECT_NAME]
# 
# This script finds all the .mxs files in MXS_DIR, renders all of them with
# Maxwell Renderer using as many cluster jobs as it can without exceeding the
# license limits, and outputs the resulting png images to OUTPUT_DIR with the
# same names, plus diagnostic output and error log files.

set -o nounset
set -o errexit

# parameters
MXS_DIR=$1 
OUTPUT_DIR=$2
NUM_NODES=$3
PROJNAME=${4-render} #optional

# function initializes variables for keeping track of file name list and thread
# number
InitFileNameList () {
  FILE_NAME_LIST=""
  NUM_FILE_NAMES=0
  THREAD_NUM=0
}

# function adds the parameter to the file name list
AddToFileNameList () {
  FILE_NAME_LIST="$1:${FILE_NAME_LIST}"
  NUM_FILE_NAMES=$((NUM_FILE_NAMES+1))
}

# function starts a job to render the current list of files using Maxwell,
# clears the list and increments the thread number
StartRenderJob () {
  THREAD_NUM=$((THREAD_NUM+1))
  echo "Starting thread $THREAD_NUM with FILE_NAME_LIST = $FILE_NAME_LIST"
  qsub -N "${PROJNAME}_thread_${THREAD_NUM}"  -l walltime=23:00:00 \
    -l nodes=1:ppn=12,mem=10gb \
    -o ${OUTPUT_DIR}/${PROJNAME}_thread_${THREAD_NUM}_output.txt \
    -e ${OUTPUT_DIR}/${PROJNAME}_thread_${THREAD_NUM}_error.txt \
    -v MXS_DIR=${MXS_DIR},MXS_NAMES=${FILE_NAME_LIST},OUTPUT_DIR=${OUTPUT_DIR} \
    ./render_thread.pbs
  FILE_NAME_LIST=""
  NUM_FILE_NAMES=0
}

# init log
echo "Running batch_render.sh"
echo "Started $(date +%F\ %T)"

# calculated constants
NUM_FILES=$(find ${MXS_DIR}/*.mxs -maxdepth 0 -type f | wc -l)
NUM_FILES_PER_NODE=$(((NUM_FILES + (NUM_NODES-1))/NUM_NODES))

# log info
echo "MXS_DIR = $MXS_DIR"
echo "OUTPUT_DIR = $OUTPUT_DIR"
echo "NUM_NODES = $NUM_NODES"
echo "PROJNAME = $PROJNAME"
echo "NUM_FILES = $NUM_FILES"
echo "NUM_FILES_PER_NODE = $NUM_FILES_PER_NODE"

InitFileNameList

# create output directory if necessary
if [ ! -d ${OUTPUT_DIR} ]
then
  mkdir ${OUTPUT_DIR}
fi

# iterate over each mxs file
for MXS_PATH in ${MXS_DIR}/*.mxs
do 
  temp=${MXS_PATH##*/}
  MXS_NAME=${temp%.*}  

  AddToFileNameList ${MXS_NAME}

  if [ $NUM_FILE_NAMES -eq $NUM_FILES_PER_NODE ]
  then
    StartRenderJob
  fi
done

# final job for leftover files
if [ $NUM_FILE_NAMES -gt 0 ]
then
  StartRenderJob
fi

echo "Ended $(date +%F\ %T)"
