#!/bin/bash
# set -euo pipefail
set -e

if [ $# -eq 0 ]
  then
    echo "
No arguments passed
Usage: bash entrypoint.sh [..]

Options:
--wait wait for other services to start (db/redis)
--migrate migrate db (alembic)
--test  run tests
--dev   run dev server
--prod  run prod server (gunicorn)
"
    exit 0
fi


while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --wait)
    WAIT=1
    shift
    ;;
    --test)
    TEST=1
    shift
    ;;
    --dev)
    DEV=1
    shift
    ;;
    --prod)
    PROD=1
    shift
    ;;
    --migrate)
    MIGRATE_DB=1
    shift
    ;;
    *)
    shift
    ;;
esac
done

if [ -n "${WAIT}" ]
then 
    CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    ${CURR_DIR}/wait-for-it.sh -t 0 ${REDIS_HOST}:${REDIS_PORT}
    ${CURR_DIR}/wait-for-it.sh -t 0 ${SOCKET_HOST}:${SOCKET_PORT}
    ${CURR_DIR}/wait-for-it.sh -t 0 ${MONGO_HOST}:${MONGO_PORT}
fi

export PYTHONPATH=.
export PYTHONUNBUFFERED=TRUE

if [ -n "${MIGRATE_DB}" ]
then
    alembic upgrade head
fi

if [ -n "${TEST}" ]
then
    pytest -p no:cacheprovider
fi

if [ -n "${DEV}" ]
then
    uvicorn app.main:app --reload --host 0.0.0.0 --port ${APPLICATION_PORT:-8000}
fi
if [ -n "${PROD}" ]
then
    gunicorn app.main:app \
        --bind 0.0.0.0:${APPLICATION_PORT:-8000} \
        -w ${APPLICATION_WORKERS:-3} \
        -k uvicorn.workers.UvicornWorker \
        --access-logfile \
        - \
        --capture-output
fi