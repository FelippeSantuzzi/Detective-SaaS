# ============================================================
#  PROJETO DETECTIVE — api_ml.py
#  Responsabilidade: buscar dados de anúncios e vendedores
#  usando a API oficial do Mercado Livre (sem Selenium).
#
#  Funciona no Streamlit Cloud pois usa só httpx (HTTP puro).
#
#  Endpoints usados:
#    GET https://api.mercadolibre.com/items/{item_id}
#    GET https://api.mercadolibre.com/users/{seller_id}
#    GET https://api.mercadolibre.com/sites/MLB/search?seller_id=...
# ============================================================

import httpx
import re


# ─────────────────────────────────────────────────────────────
# EXTRAI O ID DO ANÚNCIO A PARTIR DE UM LINK DO ML
# ─────────────────────────────────────────────────────────────

def extrair_id_do_link(url: str) -> str | None:
    """
    Extrai o ID do anúncio (ex: MLB3353330543) de qualquer
    formato de link do Mercado Livre.

    Exemplos de links suportados:
      - https://produto.mercadolivre.com.br/MLB-3353330543-...
      - https://www.mercadolivre.com.br/.../p/MLB123456
      - https://www.mercadolivre.com.br/...?item_id=MLB123456
      - https://www.mercadolivre.com.br/.../up/MLBU...?pdp_filters=item_id%3AMLB123456
    """
    if not url:
        return None

    # Prioridade 1 — wid= na query string (formato de busca do ML)
    match = re.search(r'wid=(MLB\d+)', url)
    if match:
        return match.group(1)

    # Prioridade 2 — item_id no parâmetro pdp_filters
    match = re.search(r'item_id[%3A:]+MLB(\d+)', url)
    if match:
        return f"MLB{match.group(1)}"

    # Prioridade 3 — item_id direto na query string
    match = re.search(r'item_id=MLB(\d+)', url)
    if match:
        return f"MLB{match.group(1)}"

    # Prioridade 4 — MLB com hífen no path (formato clássico)
    match = re.search(r'MLB-(\d+)', url)
    if match:
        return f"MLB{match.group(1)}"

    # Prioridade 4 — MLB sem hífen no path ou query
    match = re.search(r'MLB(\d+)', url)
    if match:
        return f"MLB{match.group(1)}"

    return None


# ─────────────────────────────────────────────────────────────
# BUSCA DADOS DO ANÚNCIO
# ─────────────────────────────────────────────────────────────

def buscar_anuncio(item_id: str) -> dict | None:
    """
    Busca os dados de um anúncio pela API oficial do ML.

    Retorna um dicionário no mesmo formato do extrator.py
    para manter compatibilidade com historico.py e alertas.py
    """
    try:
        url = f"https://api.mercadolibre.com/items/{item_id}"
        r = httpx.get(url, timeout=10)

        if r.status_code != 200:
            print(f"[API_ML] ❌ Status {r.status_code} para {item_id}")
            return None

        d = r.json()

        # Frete grátis
        frete_gratis = False
        shipping = d.get("shipping", {})
        if shipping.get("free_shipping"):
            frete_gratis = True

        # Estoque
        estoque = d.get("available_quantity")
        estoque_texto = f"{estoque} disponível(is)" if estoque else "Não informado"

        # Imagem
        imagem = ""
        pictures = d.get("pictures", [])
        if pictures:
            imagem = pictures[0].get("url", "")

        # Preço original e desconto
        preco_atual = d.get("price", 0)
        preco_original = d.get("original_price")
        desconto = "Sem desconto"
        if preco_original and preco_original > preco_atual:
            pct = round((1 - preco_atual / preco_original) * 100)
            desconto = f"{pct}% OFF"

        # Avaliações
        avaliacoes = 0
        reviews = d.get("reviews", {})
        if isinstance(reviews, dict):
            avaliacoes = reviews.get("total", 0)

        # Vendas
        vendas = f"+{d.get('sold_quantity', 0)} vendidos"

        return {
            "titulo"        : d.get("title", "Não encontrado"),
            "imagem"        : imagem,
            "link"          : d.get("permalink", ""),
            "preco"         : preco_atual,
            "preco_original": preco_original,
            "desconto"      : desconto,
            "frete_gratis"  : frete_gratis,
            "estoque"       : estoque,
            "estoque_texto" : estoque_texto,
            "avaliacoes"    : avaliacoes,
            "vendas"        : vendas,
            "vendedor_id"   : d.get("seller_id"),
            "estado"        : d.get("condition", ""),
        }

    except Exception as e:
        print(f"[API_ML] ❌ Erro: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# BUSCA DADOS DO VENDEDOR
# ─────────────────────────────────────────────────────────────

def buscar_vendedor(seller_id: int) -> dict | None:
    """Busca reputação e dados do vendedor."""
    try:
        url = f"https://api.mercadolibre.com/users/{seller_id}"
        r = httpx.get(url, timeout=10)

        if r.status_code != 200:
            return None

        d = r.json()
        rep = d.get("seller_reputation", {})

        return {
            "nome"          : d.get("nickname", ""),
            "reputacao"     : rep.get("level_id", ""),
            "vendas_totais" : rep.get("transactions", {}).get("completed", 0),
        }

    except:
        return None


# ─────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL — usada pelo dashboard
# ─────────────────────────────────────────────────────────────

def coletar_por_link(url: str) -> dict | None:
    """
    Recebe um link do ML, extrai o ID e retorna os dados
    completos do anúncio + vendedor.

    Retorna None se não conseguir extrair ou buscar.
    """
    item_id = extrair_id_do_link(url)

    if not item_id:
        print(f"[API_ML] ❌ Não foi possível extrair ID do link: {url}")
        return None

    print(f"[API_ML] 🔍 Buscando {item_id}...")
    dados = buscar_anuncio(item_id)

    if not dados:
        return None

    # Enriquece com dados do vendedor
    if dados.get("vendedor_id"):
        vendedor = buscar_vendedor(dados["vendedor_id"])
        if vendedor:
            dados["vendedor_nome"]   = vendedor["nome"]
            dados["vendedor_rep"]    = vendedor["reputacao"]
            dados["vendedor_vendas"] = vendedor["vendas_totais"]

    print(f"[API_ML] ✅ {dados['titulo']} — R$ {dados['preco']}")
    return dados


# ─────────────────────────────────────────────────────────────
# TESTE ISOLADO
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    url_teste = "https://www.mercadolivre.com.br/notebook-dell-inspiron-15-i5/p/MLB3353330543"
    print(f"Testando com: {url_teste}\n")
    dados = coletar_por_link(url_teste)
    if dados:
        for k, v in dados.items():
            print(f"  {k}: {v}")
    else:
        print("❌ Falha na coleta.")# rebuild
