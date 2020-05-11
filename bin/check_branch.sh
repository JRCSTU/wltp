#! /bin/bash
#
# SYNTAX: check-branch.sh [branch]
#
# Run it in a cloned repo with --shared to clean-test recent "master"

my_dir=`dirname "$0"`
cd "$my_dir/.."
rm -rf build/* && git fetch origin && git reset --hard origin/${1:-master} && pytest
