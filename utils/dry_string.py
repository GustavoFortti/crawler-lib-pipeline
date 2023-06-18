import re
from unidecode import unidecode

def remove_special_characters(string: str) -> str:
    """
    Remove caracteres especiais de uma string.
    :param string: A string a ser processada.
    :return: A string resultante apos a remocao dos caracteres especiais.
    """
    string = unidecode(string)
    string = re.sub(r'[^\w\s]', '', string)
    string = re.sub(r'\s+', '_', string.lower())

    return string

def fix_if_string(element: any) -> str:
    """
    Verifica se o elemento é uma string e aplica tratamentos de formatação.
    :param element: O elemento a ser verificado.
    :return: A string formatada.
    """
    return unidecode(element.lower()) if isinstance(element, str) else element