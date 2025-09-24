#!/bin/bash -ue

STRING=.pyenv

#check if this script was sourced (https://stackoverflow.com/a/28776166)
if (return 0 2>/dev/null)
then
  if grep -q $STRING  <(echo $PATH)
  then
    echo "=== Before:"
    echo $PATH | awk -F: '{for(i=1; i<=NF; i++) {printf("%s\n",$i)}}'

    export PATH=$(
      echo $PATH \
      | awk -F: '{for(i=1; i<=NF; i++) {printf("%s\n",$i)}}' \
      | grep -v $STRING \
      | tr '\n' ':' | sed 's/:$/\n/' \
    )

    echo "=== After:"
    echo $PATH | awk -F: '{for(i=1; i<=NF; i++) {printf("%s\n",$i)}}'
  else
    echo "NOTICE: PATH already clean of entries containing '$STRING'"
  fi
else
  echo "ERROR: this script needs to be sourced"
  exit 3
fi
