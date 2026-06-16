#  PROJETO DETECTIVE — extrator.py
#  Responsabilidade: receber o HTML coletado pelo coletor.py
#  e extrair os dados do concorrente usando BeautifulSoup.
#  Biblioteca usada: BeautifulSoup4
#
#  Dados extraídos:
#    - Título do produto
#    - Imagem do produto
#    - Link canônico do anúncio
#    - Preço atual (com desconto, se houver)
#    - Preço original (se houver desconto)
#    - Percentual de desconto
#    - Frete grátis (sim/não)
#    - Estoque disponível
#    - Avaliações (quantidade)
#    - Vendas (+X vendidos)


from bs4 import BeautifulSoup
import re


def extrair_dados(html):
    """
    Recebe o HTML da página do concorrente e retorna
    um dicionário com todos os dados extraídos.

    Parâmetros:
        html (str): HTML completo retornado pelo coletor.py

    Retorna:
        dict: dicionário com os dados do concorrente,
              ou None se o HTML for inválido
    """

    if not html:
        print("[EXTRATOR] ❌ HTML vazio ou inválido.")
        return None

    print("[EXTRATOR] Iniciando extração com BeautifulSoup...")
    soup = BeautifulSoup(html, "html.parser")
    dados = {}

    # ── 1. TÍTULO
    try:
        titulo = soup.find(class_="ui-pdp-title")
        dados["titulo"] = titulo.text.strip() if titulo else "Não encontrado"
    except:
        dados["titulo"] = "Erro"
    print(f"[EXTRATOR] Título    : {dados['titulo']}")

    # ── 2. IMAGEM DO PRODUTO
    try:
        galeria = soup.find(class_="ui-pdp-gallery__figure")
        if galeria:
            img = galeria.find("img")
            dados["imagem"] = img.get("src", "") if img else ""
        else:
            dados["imagem"] = ""
    except:
        dados["imagem"] = ""
    print(f"[EXTRATOR] Imagem    : {dados['imagem'][:60]}")

    # ── 3. LINK CANÔNICO DO ANÚNCIO
    # Extrai o link real da página para exibir no dashboard
    # O link canônico é sempre o endereço definitivo do anúncio
    try:
        canonical = soup.find("link", rel="canonical")
        if canonical:
            dados["link"] = canonical.get("href", "")
        else:
            og_url = soup.find("meta", property="og:url")
            dados["link"] = og_url.get("content", "") if og_url else ""
    except:
        dados["link"] = ""
    print(f"[EXTRATOR] Link      : {dados['link'][:60]}")

    # ── 4. PREÇO ATUAL
    try:
        preco_box = soup.find("div", class_="ui-pdp-price__second-line")
        if preco_box:
            fracao   = preco_box.find(class_="andes-money-amount__fraction")
            centavos = preco_box.find(class_="andes-money-amount__cents")
            valor = fracao.text.strip() if fracao else "0"
            cents = centavos.text.strip() if centavos else "00"
            dados["preco"] = float(f"{valor}.{cents}".replace(",", ""))
        else:
            fracao = soup.find(class_="andes-money-amount__fraction")
            dados["preco"] = float(fracao.text.strip()) if fracao else 0.0
    except:
        dados["preco"] = 0.0
    print(f"[EXTRATOR] Preço     : R$ {dados['preco']:.2f}")

    # ── 5. PREÇO ORIGINAL
    try:
        original_box = soup.find("div", class_="ui-pdp-price__original-value")
        if original_box:
            fracao_orig = original_box.find(class_="andes-money-amount__fraction")
            dados["preco_original"] = float(fracao_orig.text.strip()) if fracao_orig else None
        else:
            dados["preco_original"] = None
    except:
        dados["preco_original"] = None
    print(f"[EXTRATOR] Preço orig: R$ {dados['preco_original']}")

    # ── 6. DESCONTO
    try:
        desconto = soup.find(class_="andes-money-amount__discount")
        dados["desconto"] = desconto.text.strip() if desconto else "Sem desconto"
    except:
        dados["desconto"] = "Sem desconto"
    print(f"[EXTRATOR] Desconto  : {dados['desconto']}")

    # ── 7. FRETE GRÁTIS
    try:
        frete_box = soup.find(class_="ui-pdp-shipping")
        if frete_box:
            texto_frete = frete_box.text.strip().lower()
            dados["frete_gratis"] = "grátis" in texto_frete or "gratis" in texto_frete
            dados["frete_texto"] = frete_box.text.strip()[:80]
        else:
            dados["frete_gratis"] = False
            dados["frete_texto"] = "Não informado"
    except:
        dados["frete_gratis"] = False
        dados["frete_texto"] = "Erro"
    icone = "✅" if dados["frete_gratis"] else "❌"
    print(f"[EXTRATOR] Frete gr. : {icone} {dados['frete_texto'][:50]}")

    # ── 8. ESTOQUE
    try:
        estoque_box = soup.find(class_="ui-pdp-buybox__quantity")
        if estoque_box:
            texto_estoque = estoque_box.text.strip()
            dados["estoque_texto"] = texto_estoque
            match = re.search(r'\+?(\d+)\s+disponív', texto_estoque, re.IGNORECASE)
            if match:
                dados["estoque"] = int(match.group(1))
            elif "último" in texto_estoque.lower():
                dados["estoque"] = 1
            else:
                dados["estoque"] = None
        else:
            dados["estoque"] = None
            dados["estoque_texto"] = "Não informado"
    except:
        dados["estoque"] = None
        dados["estoque_texto"] = "Erro"
    print(f"[EXTRATOR] Estoque   : {dados['estoque_texto']}")

    # ── 9. AVALIAÇÕES
    try:
        avaliacoes = soup.find(class_="ui-pdp-review__amount")
        if avaliacoes:
            dados["avaliacoes"] = int(
                avaliacoes.text.strip().replace("(", "").replace(")", "")
            )
        else:
            dados["avaliacoes"] = 0
    except:
        dados["avaliacoes"] = 0
    print(f"[EXTRATOR] Avaliações: {dados['avaliacoes']}")

    # ── 10. VENDAS
    try:
        vendas = soup.find(class_="ui-pdp-subtitle")
        dados["vendas"] = vendas.text.strip() if vendas else "Não informado"
    except:
        dados["vendas"] = "Não informado"
    print(f"[EXTRATOR] Vendas    : {dados['vendas']}")

    print("[EXTRATOR] ✅ Extração concluída!")
    return dados


if __name__ == "__main__":

    print("=" * 55)
    print("   DETECTIVE — Testando extrator.py")
    print("=" * 55 + "\n")

    try:
        with open("html_selenium.txt", "r", encoding="utf-8") as f:
            html = f.read()
        print(f"HTML carregado: {len(html):,} caracteres\n")
    except FileNotFoundError:
        print("❌ html_selenium.txt não encontrado.")
        print("   Rode o coletor.py primeiro.")
        exit()

    dados = extrair_dados(html)

    if dados:
        print("\n" + "=" * 55)
        print("   DOSSIER DO CONCORRENTE")
        print("=" * 55)
        print(f"  📦 Produto  : {dados['titulo']}")
        print(f"  🖼️  Imagem   : {dados['imagem'][:60]}")
        print(f"  🔗 Link     : {dados['link'][:60]}")
        print(f"  💰 Preço    : R$ {dados['preco']:.2f}")
        if dados['preco_original']:
            print(f"  🏷️  Original : R$ {dados['preco_original']:.2f}")
        print(f"  🔖 Desconto : {dados['desconto']}")
        print(f"  🚚 Frete    : {'GRÁTIS ✅' if dados['frete_gratis'] else 'Pago ❌'}")
        print(f"  📊 Estoque  : {dados['estoque_texto']}")
        if dados['estoque'] is not None:
            if dados['estoque'] <= 5:
                print(f"  ⚠️  ALERTA   : Estoque BAIXO ({dados['estoque']} unidades)!")
            else:
                print(f"  ✅ Unidades  : {dados['estoque']}+ disponíveis")
        print(f"  ⭐ Avaliações: {dados['avaliacoes']}")
        print(f"  🏆 Vendas   : {dados['vendas']}")
        print("=" * 55)