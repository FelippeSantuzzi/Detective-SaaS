
#  PROJETO DETECTIVE — coletor.py
#  v11 — URL agrupada /up/ com filtro do anúncio específico


import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# URL agrupada com o ID do anúncio do concorrente
URL_PRODUTO = (
    "https://www.mercadolivre.com.br/"
    "mangote-termico-alta-temperatura-cozinha-industrial-par-epi/"
    "up/MLBU2046181196"
    "?pdp_filters=item_id%3AMLB5105688206"
)


TIMEOUT = 30


def pausa(minimo=2, maximo=4):
    time.sleep(random.uniform(minimo, maximo))


def criar_driver(modo_visivel=False):
    opcoes = uc.ChromeOptions()
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--window-size=1366,768")
    opcoes.add_argument("--lang=pt-BR")

    driver = uc.Chrome(
        options=opcoes,
        headless=not modo_visivel,
        # version_main removido — detecta automaticamente a versão do Chrome instalado
    )
    return driver


def buscar_pagina(url=URL_PRODUTO, modo_visivel=False):

    print("[COLETOR] Iniciando navegador...")
    driver = None

    try:
        driver = criar_driver(modo_visivel=modo_visivel)

        # Passo 1 — Home do ML para definir cookies
        print("[COLETOR] Passo 1/2 — Abrindo home do ML Brasil...")
        driver.get("https://www.mercadolivre.com.br")
        pausa(5, 7)

        # Passo 2 — Acessa a página do produto
        print(f"[COLETOR] Passo 2/2 — Acessando produto...")
        driver.get(url)
        pausa(10, 14)

        # Scroll humano
        print("[COLETOR] Simulando leitura humana...")
        for pos in [300, 600, 900, 300, 0]:
            driver.execute_script(f"window.scrollTo(0, {pos});")
            pausa(2, 3)

        url_final = driver.current_url
        print(f"[COLETOR] URL final: {url_final[:80]}")

        # Aguarda elemento do produto
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-pdp-title")),
                    EC.presence_of_element_located((By.CLASS_NAME, "andes-money-amount")),
                    EC.presence_of_element_located((By.TAG_NAME, "h1")),
                )
            )
            print("[COLETOR] Elemento do produto detectado!")
        except:
            print("[COLETOR]  Timeout — capturando mesmo assim...")

        html    = driver.page_source
        tamanho = len(html)
        print(f"[COLETOR] HTML capturado: {tamanho:,} caracteres")

        print("\n[COLETOR] Diagnóstico:")
        checks = {
            "Título (ui-pdp-title)"      : "ui-pdp-title" in html,
            "Preço (andes-money-amount)" : "andes-money-amount" in html,
            "Frete (ui-pdp-shipping)"    : "ui-pdp-shipping" in html,
            "Avaliações (ui-pdp-review)" : "ui-pdp-review" in html,
        }
        for item, encontrado in checks.items():
            print(f"   {'✅' if encontrado else '❌'} {item}")

        with open("html_selenium.txt", "w", encoding="utf-8") as f:
            f.write(html)

        return html if tamanho > 50000 else None

    except Exception as erro:
        print(f"[COLETOR] ❌ Erro: {erro}")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            print("[COLETOR] Navegador fechado.")


if __name__ == "__main__":

    print("=" * 55)
    print("   DETECTIVE — Testando coletor.py v11")
    print("=" * 55 + "\n")

    html = buscar_pagina(modo_visivel=True)

    if html:
        print(f"\n✅ {len(html):,} chars prontos para o extrator.")
    else:
        print("\n❌ Falha na coleta.")
