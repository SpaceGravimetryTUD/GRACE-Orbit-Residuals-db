#!/bin/bash -ue

function echo-red(){
  echo $'\e[91m'"$@"$'\e[0m'
}

DIR=$(cd $(dirname $BASH_SOURCE);pwd)

if [ ! -s $DIR/.env ]
then
  echo-red "ERROR: cannot find $DIR/.env file. One example of this file can be found in the README.md"
  exit 3
fi

source $DIR/.env

while [[ $# -gt 0 ]]
do
  OP="$1"
  case "$OP" in
  modes|help|-help|--help|h|-h) #shows all available modes
    echo "NOTICE: 'option's must come before 'operation's"
    grep ') #' $BASH_SOURCE  \
      | grep -v grep \
      | sed 's:)::g' \
      | column -t -s\#
    exit
  ;;
  -x) #option: set -x
    set -x
  ;;
  install) #operation: install necessary software
    #get packages
    sudo apt-get install postgresql-client-common postgresql-client podman pipx
    pip3 install podman-compose
    #Check
    podman-compose -v
    pipx ensurepath
    # Install and check poetry
    pipx install poetry
    poetry -V
  ;;
  env) #operation: show the values of the variables in the .env file
    for i in $(cat $DIR/.env | sed 's:#.*::g' | sed '/^$/d' | awk -F= '{print $1}')
    do
      eval 'echo '$i'=${'$i'}'
    done
  ;;
  stop|down) #operation: turn off the db; NOTICE that 'stop' and 'down' are different things!
    _CONTAINER_NAME=$(awk  '/container_name:/ {print $2}' $DIR/docker-compose.yml)
    if grep -q $_CONTAINER_NAME <(podman ps --noheading  | awk '{print $NF'})
    then
      podman-compose -f $DIR/docker-compose.yml $OP
    else
      echo-red "No container $_CONTAINER_NAME currently running:"
    fi
    podman ps
  ;;
  start|up) #operation: turn on the db; NOTICE that 'start' and 'up' are different things!
    _CONTAINER_NAME=$(awk  '/container_name:/ {print $2}' $DIR/docker-compose.yml)
    if grep -q $_CONTAINER_NAME <(podman ps --noheading  | awk '{print $NF'})
    then
      echo-red "Container $_CONTAINER_NAME already running:"
    else
      podman-compose -f $DIR/docker-compose.yml $OP $([ "$OP" ==  "up" ] && echo '-d')
    fi
    podman ps
  ;;
  ps) #operation: podman ps
    podman ps
  ;;
  -l) #operation: list tables
    _USER=$(    awk  '/POSTGRES_USER:/     {print $2}' $DIR/docker-compose.yml)
    _PASSWORD=$(awk  '/POSTGRES_PASSWORD:/ {print $2}' $DIR/docker-compose.yml)
    psql -l -p $EXTERNAL_PORT -h 127.0.0.1 -U $_USER -W $_PASSWORD
  ;;
  run) #operation: run all following arguments and exit
    poetry run ${@:2}
    exit
  ;;
  load) #operation: load the files given by the following arguments and exit
    for i in "${@:2}"
    do
      poetry run python scripts/init_db.py --use_batches --filepath "$i"
    done
    exit
  ;;
  check-schema) #operation: verify schema from inside the container
    podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "\d $TABLE_NAME;"
  ;;
  postgis) #operation: enable PostGIS
    podman exec -it postgis_container psql -U user -d $DATABASE_NAME -c "CREATE EXTENSION postgis;"
  ;;
  test-query) #operation: run a simple query
    poetry run python scripts/space_time_query.py
  ;;
  run-tests) #operation: run the tests
    poetry run pytest
  ;;
  list-ports) #operation: list open ports and associated processes
    sudo ss -ltnp
  ;;
  *)
    echo-red "WARNING: ignored argument '$OP'"
  ;;
  esac
  #shift to next argument
  shift
done
