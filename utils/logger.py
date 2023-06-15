import logging

def setup_logger() -> object:
    # Configuracao basica do log
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()])
    
    # Criando um logger
    return logging.getLogger('crawler-lib-pipeline')