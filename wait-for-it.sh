#!/usr/bin/env bash

set -e

host="$1"
shift
cmd="$@"

until nc -z "$DATABASE_HOST" 5432; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python3 manage.py migrate
python3 manage.py collectstatic --noinput
>&2 echo "Postgres is up - executing command"
exec $cmd