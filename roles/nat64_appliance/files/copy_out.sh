#!/bin/bash

# A script to be used as the entrypoint in a container to copy out files from the container
# to a mounted directory. SRC_DIR and CHECKSUM_FILE are expected to be set correctly
# in the container image. When creating a container, a volume mount must be provided which
# mounts as the value of DEST_DIR (/target) inside the container.
#
# The files to copy are determined by the entries in the checksum file. Copying is skipped
# if the same checksum file DEST_DIR has a matching entry. Resulting destination files
# are checked with sha256sum.
#
# This script is limited to what is available in centos and ubi minimal container images
set -eu

SRC_DIR=${SRC_DIR:-/usr/share/images}
DEST_DIR=${DEST_DIR:-/target}
CHECKSUM_FILE=${CHECKSUM_FILE:-}

if [ ! -d $DEST_DIR ]; then
    echo "$DEST_DIR is not a directory, mount $DEST_DIR into the container or set DEST_DIR to a mounted directory to copy files into"
    exit 1
fi

if [ ! -d $SRC_DIR ]; then
    echo "$SRC_DIR is not a directory, rebuild the image with files in $SRC_DIR or set SRC_DIR to the location of files to copy out"
    exit 1
fi

if [ -z $CHECKSUM_FILE ]; then
    echo "CHECKSUM_FILE needs to be set to a checksum file in $SRC_DIR, cannot copy files"
    exit 1
fi

src_checksum=${SRC_DIR%%/}/${CHECKSUM_FILE}

if [ ! -f $src_checksum ]; then
    echo "Checksum file $src_checksum does not exist, cannot copy files"
    exit 1
fi

dest_checksum=${DEST_DIR%%/}/${CHECKSUM_FILE}
touch $dest_checksum
while read -r checksum_entry; do
    file_name=$(echo "$checksum_entry" | cut -d " " -f 3)
    src_file_name=${SRC_DIR%%/}/${file_name}
    dest_file_name=${DEST_DIR%%/}/${file_name}
    if [ ! -f $dest_file_name ]; then
        echo "$dest_file_name does not exist, copying"
        do_copy=1
    elif grep -Fxq "$checksum_entry" $dest_checksum ; then
        echo "$file_name checksum matches in $dest_checksum, skipping"
        do_copy=0
    else
        echo "$file_name checksum failed match in $dest_checksum, copying"
        do_copy=1
    fi
    if [[ $do_copy -eq 1 ]]; then
        cp -v $src_file_name $dest_file_name
    fi
done < $src_checksum
cp -v $src_checksum $dest_checksum
sha256sum -c $dest_checksum
