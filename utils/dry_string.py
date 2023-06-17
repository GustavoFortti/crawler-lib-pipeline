import re
import unidecode

def remove_special_characters(string: str) -> str:
    """
    Remove caracteres especiais de uma string.
    :param string: A string a ser processada.
    :return: A string resultante apos a remocao dos caracteres especiais.
    """
    string = unidecode.unidecode(string)
    string = re.sub(r'[^\w\s]', '', string)
    string = re.sub(r'\s+', '_', string.lower())

    return string