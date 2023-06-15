import argparse

def arg_parser() -> dict:
    """
    Realiza a analise dos argumentos da linha de comando.
    :return: Um dicionario contendo os valores dos argumentos.
    """
    parser = argparse.ArgumentParser(description='Descricao do script')

    parser.add_argument('--env', type=str, help='Ambiente definido (dev, exp, prd)')
    parser.add_argument('--job_name', type=str, help='nome do processo (ex: vivareal)')
    parser.add_argument('--job_exec_type', type=str, help='tipo de execução do processo (ex: dataminner)')
    parser.add_argument('--driver', type=str, help='driver do selenium (chrome, firefox)')
    parser.add_argument('--driver_path', type=str, help='caminho do driver')
    parser.add_argument('--master', type=str, help='plataforma de execucao (ex: local-selenium)')
    parser.add_argument('--uri', type=str, help='Endereco do servidor')

    args = parser.parse_args()

    CONFIG = {"env": args.env,
            "job_name": args.job_name,
            "job_exec_type": args.job_exec_type,
            "driver": args.driver,
            "driver_path": args.driver_path,
            "uri": args.uri,
            "master": args.master}

    return CONFIG