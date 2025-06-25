#!/bin/bash -ue

function echo-red(){
  echo $'\e[91m'"$@"$'\e[0m'
}

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
  down) #operation: turn off the db
    podman-compose down
  ;;
  up) #operation: turn on the db
    podman-compose -f docker-compose.yml up -d
  ;;
  ps) #operation: podman ps
    podman ps
  ;;
  run) #operation: run all following arguments and exit
    poetry run ${2:}
    exit
  ;;
  load) #operation: load the files given by the following arguments and exit
    for i in "${2:}"
    do
      poetry run python scripts/init_db.py --use_batches --filepath "$i"
    done
    exit
  ;;
  check-schema) #operation: verify schema from inside the container
    podman exec -it postgis_container psql -U user -d geospatial_db -c "\d kbr_gravimetry;"
  ;;
  postgis) #operation: enable PostGIS
    podman exec -it postgis_container psql -U user -d geospatial_db -c "CREATE EXTENSION postgis;"
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
