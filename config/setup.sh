#!/bin/bash

install_pip() {
    if command -v pip >/dev/null 2>&1; then
    echo "O pip esta instalado."
    else
        sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py
        pip3 --version
    fi

}

install_lib() {
    local lib=$1
    if ! pip show "$lib" >/dev/null 2>&1; then
        echo "Instalando $lib..."
        if pip install "$lib"; then
            echo "Instalacao de $lib concluída com sucesso."
        else
            echo "Falha ao instalar $lib."
        fi
    else
        echo "$lib ja esta instalada."
    fi
}

install_sys() {
    local lib=$1
    if command -v "$lib" >/dev/null 2>&1; then
        echo "O pip esta instalado."
    else
        if sudo apt-get install -y "$lib"; then
            echo "Instalacao de $lib concluída com sucesso."
        else
            echo "Falha ao instalar $lib."
        fi
    fi
}

install_from_requirements() {
    local requirements_file=$1
    local install_file=$2
    echo $requirements_file
    if [ -f "$requirements_file" ]; then
        while IFS= read -a lib || [[ -n "$lib" ]]; do
            eval $install_file "$lib"
        done < "$requirements_file"
    else
        echo "Arquivo $requirements_file nao encontrado."
    fi
}