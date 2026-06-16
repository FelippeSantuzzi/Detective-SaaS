# ============================================================
#  PROJETO DETECTIVE — historico.py
#  Responsabilidade: receber o dicionário de dados extraído
#  pelo extrator.py e salvar em CSV com timestamp.
#
#  Biblioteca usada: csv e datetime (já vêm com o Python)
#
#  Por que CSV?
#  Simples, leve, abre no Excel e no Streamlit.
#  Cada linha = uma execução do DETECTIVE no tempo.
#  Com isso criamos o histórico de preços do concorrente.
#
#  Estrutura do CSV gerado:
#  data_hora | titulo | preco | preco_original | desconto |
#  frete_gratis | estoque | avaliacoes | vendas
# ============================================================

import csv
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────

ARQUIVO_CSV = os.path.join(os.path.dirname(__file__), "historico_concorrente.csv")

COLUNAS = [
    "data_hora",
    "titulo",
    "imagem",
    "link",
    "preco",
    "preco_original",
    "desconto",
    "frete_gratis",
    "estoque",
    "estoque_texto",
    "avaliacoes",
    "vendas",
]

# ─────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────

def salvar_historico(dados):
    """
    Recebe o dicionário de dados do extrator.py e salva
    uma nova linha no CSV com a data e hora atual.

    Se o CSV não existir, cria com cabeçalho.
    Se já existir, apenas adiciona uma nova linha.

    Parâmetros:
        dados (dict): dicionário retornado pelo extrator.py

    Retorna:
        str: caminho do arquivo CSV salvo
    """

    if not dados:
        print("[HISTORICO] ❌ Dados inválidos — nada a salvar.")
        return None

    # Adiciona o timestamp ao dicionário
    dados["data_hora"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Verifica se o CSV já existe para saber se precisa do cabeçalho
    arquivo_existe = os.path.exists(ARQUIVO_CSV)

    try:
        # 'a' = append — adiciona ao final sem apagar o que já existe
        with open(ARQUIVO_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore")

            # Escreve o cabeçalho só se o arquivo for novo
            if not arquivo_existe:
                writer.writeheader()
                print(f"[HISTORICO] 📁 Novo arquivo criado: {ARQUIVO_CSV}")
            else:
                print(f"[HISTORICO] 📁 Adicionando ao histórico existente: {ARQUIVO_CSV}")

            writer.writerow(dados)

        print(f"[HISTORICO] ✅ Registro salvo em: {dados['data_hora']}")
        print(f"[HISTORICO]    Preço registrado : R$ {dados.get('preco', '?')}")
        print(f"[HISTORICO]    Estoque registrado: {dados.get('estoque_texto', '?')}")
        return ARQUIVO_CSV

    except Exception as erro:
        print(f"[HISTORICO] ❌ Erro ao salvar: {erro}")
        return None


def carregar_historico():
    """
    Lê o CSV e retorna uma lista de dicionários.
    Usado pelo dashboard.py para exibir o histórico.

    Retorna:
        list: lista de dicionários com todos os registros,
              ou lista vazia se o arquivo não existir
    """

    if not os.path.exists(ARQUIVO_CSV):
        print(f"[HISTORICO] ⚠️  Arquivo {ARQUIVO_CSV} não encontrado.")
        return []

    try:
        with open(ARQUIVO_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            registros = list(reader)

        print(f"[HISTORICO] 📊 {len(registros)} registro(s) no histórico.")
        return registros

    except Exception as erro:
        print(f"[HISTORICO] ❌ Erro ao carregar: {erro}")
        return []


def resumo_historico():
    """
    Exibe um resumo do histórico — útil para o dashboard.

    Retorna:
        dict com: total_registros, preco_minimo,
                  preco_maximo, primeira_coleta, ultima_coleta
    """

    registros = carregar_historico()

    if not registros:
        return None

    precos = []
    for r in registros:
        try:
            precos.append(float(r["preco"]))
        except:
            pass

    return {
        "total_registros" : len(registros),
        "preco_minimo"    : min(precos) if precos else None,
        "preco_maximo"    : max(precos) if precos else None,
        "primeira_coleta" : registros[0]["data_hora"],
        "ultima_coleta"   : registros[-1]["data_hora"],
    }


# ─────────────────────────────────────────────────────────────
# TESTE ISOLADO
# Usa os dados reais que já extraímos do concorrente
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 55)
    print("   DETECTIVE — Testando historico.py")
    print("=" * 55 + "\n")

    # Simula os dados reais capturados pelo extrator.py
    # (em produção esses dados vêm do extrator de verdade)
    dados_teste = {
        "titulo"        : "Mangote Térmico Industrial Alta Temperatura Cozinha Par Epi",
        "preco"         : 145.41,
        "preco_original": 197.0,
        "desconto"      : "26% OFF",
        "frete_gratis"  : True,
        "estoque"       : 25,
        "estoque_texto" : "Quantidade:1 unidade(+25 disponíveis)",
        "avaliacoes"    : 15,
        "vendas"        : "Novo  |  +100 vendidos",
    }

    print("Salvando registro de teste...")
    arquivo = salvar_historico(dados_teste)

    if arquivo:
        print(f"\n✅ Dados salvos em: {arquivo}")

        # Mostra o resumo
        resumo = resumo_historico()
        if resumo:
            print("\n── Resumo do Histórico ──────────────────────────")
            print(f"   Total de registros : {resumo['total_registros']}")
            print(f"   Preço mínimo       : R$ {resumo['preco_minimo']:.2f}")
            print(f"   Preço máximo       : R$ {resumo['preco_maximo']:.2f}")
            print(f"   Primeira coleta    : {resumo['primeira_coleta']}")
            print(f"   Última coleta      : {resumo['ultima_coleta']}")
            print("─" * 50)

        print(f"\n💡 Rode o script mais vezes para acumular histórico.")
        print(f"   Cada execução adiciona uma linha nova no CSV.")
        print(f"   Abra o {arquivo} no Excel para visualizar!")