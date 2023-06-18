function check_database_port(){
    CMD=$1
    DATABASE=$2
    initial_port=$3
    final_port=$((initial_port + 10))
    ports=()

    for ((port=initial_port; port<=final_port; port++))
    do
        ports+=("$port")
    done

    PORT=""
    aux_port="my_port"
    for ((port=initial_port; port<=final_port; port++))
    do  
        CMD="${CMD//$aux_port/$port}"
        aux_port=$port
        output=$(eval $CMD)
        status=$?
        if [ $status -eq 0 ] && [ "$output" != "Unauthorized" ]; then
            EXPORT="export ${DATABASE}_PORT="$port""
            PORT="$port"
            echo $EXPORT
            eval $EXPORT
            echo "$DATABASE is connected on port $port"
            break
        fi
    done

    if [ -z "$PORT" ]; then
        echo "Nenhuma porta do $DATABASE está disponível"
    fi
}