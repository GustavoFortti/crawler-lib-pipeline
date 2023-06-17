import time
import re
import json
import requests
import unidecode

from shared.selenium import Selenium
from shared.filesystem import FileSystem
from shared.cryptography import create_hash_sha256, encode_url_base64
from utils.dry_string import remove_special_characters
from fake_useragent import UserAgent

from jobs.vivareal.config import JOB_CONFIG

class DataMiner():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe DataMiner.
        :param env_config: Dicionario contendo as configuracoes do ambiente.
        """
        self.env_config = env_config
        self.driver_type = self.env_config["driver"]
        self.driver_path = self.env_config['driver_path']

        self.index = JOB_CONFIG['default']["name"]

        self.fs = FileSystem(env_config)

    def minner(self) -> None:
        """
        Realiza a mineracao de dados.
        """
        domain = JOB_CONFIG['default']["domain"]
        href = JOB_CONFIG['sets'][0]["href"]
        url = f"{domain}{href}"

        driver = Selenium(self.driver_type, self.driver_path)
        soup = driver.get_html(url)
        href_items = self.page_find_itens(soup)
        driver.quit()

        for href in href_items:
            driver = Selenium(self.driver_type, self.driver_path)

            url = f"{domain}{href}"
            soup = driver.get_html(url)
            if (soup == None): continue

            item_page = self.page_extract_itens(soup)

            item_page['url'] = url
            item_page["id"] = encode_url_base64(item_page['codigo'])

            self.fs.save(item_page, JOB_CONFIG['bulkload']["file-format"])

            driver.quit()

    def page_find_itens(self, soup: object) -> list:
        """
        Encontra os itens da pagina.
        :param soup: O objeto BeautifulSoup contendo o HTML da pagina.
        :return: Lista de URLs encontradas.
        """
        elements = []
        for a in soup.find_all('a'):
            href = a.get("href")
            if ("/imovel/" in href):
                elements.append(href)

        return list(set(elements))

    def page_extract_itens(self, soup: object) -> dict:
        """
        Extrai os itens da pagina.
        :param soup: O objeto BeautifulSoup contendo o HTML da pagina.
        :return: Dicionario contendo as informacoes extraidas da pagina.
        """
        property_info = {}

        # Extrair informacoes do titulo
        title_element = soup.find(class_='title__title')
        property_info['titulo'] = title_element.text.strip() if title_element else ''

        # Extrair codigo
        code_element = soup.find(class_='title__code')
        property_info['codigo'] = code_element.text.strip() if code_element else ''

        # Extrair endereco
        address_element = soup.find(class_='title__address')
        property_info['endereco'] = address_element.text.strip() if address_element else ''

        # Extrair caracteristicas
        features = soup.find_all(class_='features__item')
        for feature in features:
            feature_type = self.remove_special_characters(feature['title'])
            feature_value = feature.text.strip()
            property_info[feature_type] = feature_value

        # Extrair caracteristicas adicionais
        additional_features_element = soup.find(class_='amenities__list')
        additional_features = [feature.text.strip() for feature in additional_features_element.find_all('li')] if additional_features_element else []
        property_info['caracteristicas_adicionais'] = additional_features

        # Extrair descricao
        description_element = soup.find(class_='description__text')
        property_info['descricao'] = description_element.text.strip() if description_element else ''

        # Extrair preco de venda
        price_element = soup.find(class_='price__price-info')
        property_info['preco'] = price_element.text.strip() if price_element else ''

        # Extrair valor do condominio
        condominium_element = soup.find(class_='price__list-value condominium')
        property_info['valor_condominio'] = condominium_element.text.strip() if condominium_element else ''

        # Extrair valor do IPTU
        iptu_element = soup.find(class_='price__list-value iptu')
        property_info['valor_iptu'] = iptu_element.text.strip() if iptu_element else ''

        self.save_images(property_info, soup, False)

        return property_info

    def save_images(self, property_info: dict, soup: object, download: bool) -> None:
        """
        Salva as imagens do imovel.
        :param property_info: Dicionario contendo as informacoes do imovel.
        :param soup: O objeto BeautifulSoup contendo o HTML da pagina.
        :param download: Indica se as imagens devem ser baixadas ou apenas suas URLs devem ser salvas.
        """
        image_urls = []
        carousel_container = soup.find(class_='carousel__container')
        if carousel_container:
            carousel_slides = carousel_container.find_all('li', class_='carousel__slide')
            for slide in carousel_slides:
                image_element = slide.find('img', class_='carousel__image')
                if image_element and 'src' in image_element.attrs:
                    image_link = image_element['src']
                    image_urls.append(image_link)

        sizes = [self.change_image_size(url) for url in image_urls]
        max_size = self.find_max_image_size(sizes)

        for index, url in enumerate(image_urls):
            new_url = re.sub(r'\d+x\d+', max_size, url)
            file_type = self.get_image_type_from_url(new_url)
            file_name = encode_url_base64(new_url)
            uri = self.env_config["uri"]

            if self.validate_image(url):
                if (download):
                    self.download_image(new_url, f"{uri}{file_name}.{file_type}")
                image_urls[index] = new_url
            else:
                if (download):
                    self.download_image(url, f"{uri}{file_name}.{file_type}")

        property_info["image_urls"] = image_urls

    def change_image_size(self, url: str) -> str:
        """
        Altera o tamanho da imagem na URL.
        :param url: A URL da imagem.
        :return: O tamanho da imagem modificado.
        """
        pattern = r"(\d+x\d+)"

        match = re.search(pattern, url)
        if match:
            image_size = match.group(1)
            return image_size
        else:
            print("Image size not found.")
            return ''

    def find_max_image_size(self, sizes: str) -> str:
        """
        Encontra o tamanho maximo entre uma lista de tamanhos de imagem.
        :param sizes: A lista de tamanhos de imagem.
        :return: O tamanho maximo encontrado.
        """
        max_size = None

        for size in sizes:
            width, height = map(int, size.split('x'))
            if max_size is None or width * height > max_size[0] * max_size[1]:
                max_size = (width, height)

        return f"{max_size[0]}x{max_size[1]}"

    def validate_image(self, url: str) -> bool:
        """
        Valida se uma URL corresponde a uma imagem valida.
        :param url: A URL da imagem.
        :return: True se a URL corresponder a uma imagem valida, False caso contrario.
        """
        try:
            user_agent = UserAgent()
            headers = {'User-Agent': user_agent.random}
            response = requests.head(url, headers=headers)
            return response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/')
        except requests.exceptions.RequestException:
            pass
        return False

    def download_image(self, url: str, save_path: str) -> bool:
        """
        Baixa uma imagem da URL e a salva em um caminho especifico.
        :param url: A URL da imagem.
        :param save_path: O caminho onde a imagem sera salva.
        :return: True se o download e a salvamento forem bem-sucedidos, False caso contrario.
        """
        try:
            user_agent = UserAgent()
            headers = {'User-Agent': user_agent.random}
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except requests.exceptions.RequestException:
            pass
        return False

    def get_image_type_from_url(self, url: str) -> str:
        """
        Obtem o tipo de imagem com base na URL.
        :param url: A URL da imagem.
        :return: O tipo de imagem.
        """
        file_extension = url.split(".")[-1]
        return file_extension

def run(env_config: dict) -> None:
    start_time = time.time()

    if (env_config["env"] in ["dev", "exp"]):
        crawler = DataMiner(env_config)
        crawler.minner()
    elif (env_config["env"] in ["prd"]):
        prd(env_config)
    else:
        print("Definir ambiente de execucao")
        
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execucao: {execution_time} segundos")

def prd(env_config: dict) -> None:
    try:
        DataMiner(env_config)
    except Exception as e:
        print(f"Ocorreu um erro durante a execucao da funcao job: {str(e)}")
