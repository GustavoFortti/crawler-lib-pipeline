#!/bin/bash

source $LOCAL/config/database-connection-test.sh

export ELASTIC_HOST="127.0.0.1"
export ELASTIC_PORT="9200"
export ELASTIC_USER="elastic"
export ELASTIC_PASS=$(kubectl get secrets --namespace=default elasticsearch-master-credentials -ojsonpath='{.data.password}' | base64 -d)
ELASTIC_TEST="timeout 1 curl -u \"$ELASTIC_USER:$ELASTIC_PASS\" -k \"https://localhost:my_port\" 2>/dev/null"
check_database_port "$ELASTIC_TEST" "ELASTIC" "$ELASTIC_PORT"

# export POSTGRES_HOST=$(kubectl get service postgresql -n default -o jsonpath='{.spec.clusterIP}')
# export POSTGRES_PORT="5432"
# export POSTGRES_DB="postgres"
# export POSTGRES_USER="postgres"
# export POSTGRES_PASS=$(kubectl get secret --namespace default postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
# POSTGRES_TEST="kubectl run postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:15.3.0-debian-11-r7 --env='PGPASSWORD=$POSTGRES_PASS' --command -- psql --host $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -p $POSTGRES_PORT -c 'SELECT 1;'"
# check_database_port "$POSTGRES_TEST" "POSTGRES" "$POSTGRES_PORT"
# kubectl delete pod postgresql-client --namespace default