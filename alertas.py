# ============================================================
#  PROJETO DETECTIVE — alertas.py
#  Responsabilidade: comparar o estado ATUAL do concorrente
#  com o estado ANTERIOR salvo no CSV e gerar alertas
#  para qualquer mudança detectada.
#
#  Sem biblioteca externa — usa só Python puro.
#
#  Alertas gerados:
#    🔴 CRÍTICO  → estoque zerou ou frete grátis ativado
#    🟡 ATENÇÃO  → preço caiu ou desconto aumentou
#    🟢 POSITIVO → preço subiu, estoque caiu, nota caiu
#    ℹ️  INFO     → primeira coleta, sem mudanças
# ============================================================

from historico import carregar_historico


# ─────────────────────────────────────────────────────────────
# LIMIARES DE ALERTA
# Ajuste conforme sua estratégia de negócio
# ─────────────────────────────────────────────────────────────

ESTOQUE_CRITICO   = 5     # unidades — abaixo disso é alerta crítico
VARIACAO_PRECO    = 2.0   # reais — diferença mínima para gerar alerta


# ─────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────

def verificar_alertas(dados_atual):
    """
    Compara os dados atuais com o último registro do CSV
    e retorna uma lista de alertas gerados.

    Parâmetros:
        dados_atual (dict): dicionário do extrator.py

    Retorna:
        list: lista de dicionários com os alertas,
              cada um com: nivel, emoji, titulo, mensagem, acao
    """

    alertas = []

    if not dados_atual:
        return alertas

    # Carrega o histórico para pegar o estado anterior
    historico = carregar_historico()

    # ── Primeira execução — sem histórico para comparar ──────
    if len(historico) < 2:
        alertas.append({
            "nivel"   : "info",
            "emoji"   : "ℹ️",
            "titulo"  : "Primeira coleta registrada",
            "mensagem": f"Preço inicial: R$ {dados_atual.get('preco', '?')} | "
                        f"Estoque: {dados_atual.get('estoque_texto', '?')}",
            "acao"    : "Nenhuma ação necessária. Baseline estabelecido.",
        })
        return alertas

    # Pega o penúltimo registro como "estado anterior"
    anterior = historico[-2]

    # ── 1. ALERTA DE PREÇO ───────────────────────────────────
    try:
        preco_atual    = float(dados_atual.get("preco", 0))
        preco_anterior = float(anterior.get("preco", 0))
        diferenca      = preco_atual - preco_anterior

        if abs(diferenca) >= VARIACAO_PRECO:
            if diferenca < 0:
                # Concorrente BAIXOU o preço — atenção!
                alertas.append({
                    "nivel"   : "atencao",
                    "emoji"   : "🟡",
                    "titulo"  : "Concorrente BAIXOU o preço!",
                    "mensagem": f"Era R$ {preco_anterior:.2f} → agora R$ {preco_atual:.2f} "
                                f"(queda de R$ {abs(diferenca):.2f})",
                    "acao"    : "Avalie se precisa ajustar seu preço para manter competitividade.",
                })
            else:
                # Concorrente SUBIU o preço — oportunidade!
                alertas.append({
                    "nivel"   : "positivo",
                    "emoji"   : "🟢",
                    "titulo"  : "Concorrente SUBIU o preço!",
                    "mensagem": f"Era R$ {preco_anterior:.2f} → agora R$ {preco_atual:.2f} "
                                f"(alta de R$ {diferenca:.2f})",
                    "acao"    : "Oportunidade! Você pode subir seu preço também.",
                })
    except:
        pass

    # ── 2. ALERTA DE ESTOQUE ─────────────────────────────────
    try:
        estoque_atual    = dados_atual.get("estoque")
        estoque_anterior = anterior.get("estoque")

        # Converte para int se possível
        if estoque_anterior and str(estoque_anterior).isdigit():
            estoque_anterior = int(estoque_anterior)
        else:
            estoque_anterior = None

        if estoque_atual is not None:
            # Estoque crítico — poucas unidades
            if estoque_atual <= ESTOQUE_CRITICO:
                alertas.append({
                    "nivel"   : "critico",
                    "emoji"   : "🔴",
                    "titulo"  : "Estoque do concorrente CRÍTICO!",
                    "mensagem": f"Apenas {estoque_atual} unidade(s) disponível(is).",
                    "acao"    : "🚀 AÇÃO IMEDIATA: Suba seu preço! Lei da oferta e procura — "
                                "você logo será o único vendedor disponível.",
                })

            # Estoque caindo
            elif estoque_anterior and estoque_atual < estoque_anterior:
                alertas.append({
                    "nivel"   : "positivo",
                    "emoji"   : "🟢",
                    "titulo"  : "Estoque do concorrente está CAINDO",
                    "mensagem": f"Era {estoque_anterior} → agora {estoque_atual} unidades.",
                    "acao"    : "Fique de olho. Se continuar caindo, prepare-se para subir seu preço.",
                })

            # Estoque zerou
            elif estoque_atual == 0:
                alertas.append({
                    "nivel"   : "critico",
                    "emoji"   : "🔴",
                    "titulo"  : "Concorrente SEM ESTOQUE!",
                    "mensagem": "O concorrente ficou sem produto disponível.",
                    "acao"    : "🚀 AÇÃO IMEDIATA: Suba seu preço agora! "
                                "Você é o único vendedor disponível no momento.",
                })
    except:
        pass

    # ── 3. ALERTA DE FRETE ───────────────────────────────────
    try:
        frete_atual    = str(dados_atual.get("frete_gratis", "")).lower()
        frete_anterior = str(anterior.get("frete_gratis", "")).lower()

        frete_ativo_agora  = frete_atual in ["true", "1", "sim"]
        frete_ativo_antes  = frete_anterior in ["true", "1", "sim"]

        if frete_ativo_agora and not frete_ativo_antes:
            alertas.append({
                "nivel"   : "critico",
                "emoji"   : "🔴",
                "titulo"  : "Concorrente ATIVOU frete grátis!",
                "mensagem": "O concorrente passou a oferecer frete grátis.",
                "acao"    : "Avalie oferecer frete grátis também ou compensar com preço menor.",
            })

        elif not frete_ativo_agora and frete_ativo_antes:
            alertas.append({
                "nivel"   : "positivo",
                "emoji"   : "🟢",
                "titulo"  : "Concorrente REMOVEU frete grátis!",
                "mensagem": "O concorrente deixou de oferecer frete grátis.",
                "acao"    : "Vantagem sua se você ainda oferece! Destaque isso no seu anúncio.",
            })
    except:
        pass

    # ── 4. ALERTA DE AVALIAÇÕES ──────────────────────────────
    try:
        aval_atual    = int(dados_atual.get("avaliacoes", 0))
        aval_anterior = int(anterior.get("avaliacoes", 0))

        if aval_atual > aval_anterior:
            novas = aval_atual - aval_anterior
            alertas.append({
                "nivel"   : "info",
                "emoji"   : "ℹ️",
                "titulo"  : f"Concorrente recebeu {novas} nova(s) avaliação(ões)",
                "mensagem": f"Total: {aval_anterior} → {aval_atual} avaliações.",
                "acao"    : "Verifique se as novas avaliações são positivas ou negativas.",
            })
    except:
        pass

    # ── Sem mudanças ─────────────────────────────────────────
    if not alertas:
        alertas.append({
            "nivel"   : "info",
            "emoji"   : "✅",
            "titulo"  : "Nenhuma mudança detectada",
            "mensagem": f"Preço mantido em R$ {dados_atual.get('preco', '?')} | "
                        f"Estoque estável.",
            "acao"    : "Nenhuma ação necessária.",
        })

    return alertas


def exibir_alertas(alertas):
    """
    Exibe os alertas no terminal de forma formatada.
    No dashboard.py esses mesmos dados viram cards coloridos.
    """

    print("\n" + "=" * 55)
    print("   🚨 CENTRAL DE ALERTAS DO DETECTIVE")
    print("=" * 55)

    for a in alertas:
        print(f"\n{a['emoji']}  {a['titulo']}")
        print(f"   📋 {a['mensagem']}")
        print(f"   ⚡ AÇÃO: {a['acao']}")

    print("\n" + "=" * 55)


# ─────────────────────────────────────────────────────────────
# TESTE ISOLADO
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 55)
    print("   DETECTIVE — Testando alertas.py")
    print("=" * 55 + "\n")

    # Simula dados atuais com mudanças em relação ao histórico
    # Para testar, mudamos o preço e o estoque
    dados_simulados = {
        "titulo"        : "Mangote Térmico Industrial Alta Temperatura Cozinha Par Epi",
        "preco"         : 139.90,   # ← era 145.41 — BAIXOU!
        "preco_original": 197.0,
        "desconto"      : "29% OFF",
        "frete_gratis"  : True,
        "estoque"       : 3,        # ← era 25 — CRÍTICO!
        "estoque_texto" : "Quantidade:1 unidade(+3 disponíveis)",
        "avaliacoes"    : 17,       # ← era 15 — novas avaliações!
        "vendas"        : "Novo  |  +100 vendidos",
    }

    print("Dados simulados para teste:")
    print(f"  Preço   : R$ {dados_simulados['preco']} (era R$ 145.41)")
    print(f"  Estoque : {dados_simulados['estoque']} unidades (era 25)")
    print(f"  Aval.   : {dados_simulados['avaliacoes']} (eram 15)\n")

    alertas = verificar_alertas(dados_simulados)
    exibir_alertas(alertas)