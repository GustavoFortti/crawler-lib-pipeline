import argparse

def arg_parser():
    # Cria um objeto de análise de argumentos
    parser = argparse.ArgumentParser(description='Descrição do script')

    # Adiciona os argumentos
    parser.add_argument('--env', type=str, help='Ambiente definido (dev, exp, prd)')
    parser.add_argument('--job_name', type=str, help='nome do processo (ex: vivareal)')
    parser.add_argument('--driver', type=str, help='driver do selenium (chrome, firefox)')
    parser.add_argument('--driver_path', type=str, help='caminho do driver')
    parser.add_argument('--master', type=str, help='plataforma de execução (ex: local-selenium)')
    parser.add_argument('--uri', type=str, help='Endereço do servidor')

    # Faz o parse dos argumentos da linha de comando
    args = parser.parse_args()

    # Acesso aos valores dos argumentos
    CONFIG = {"env": args.env,
            "job_name": args.job_name,
            "driver": args.driver,
            "driver_path": args.driver_path,
            "uri": args.uri,
            "master": args.master}

    return CONFIG