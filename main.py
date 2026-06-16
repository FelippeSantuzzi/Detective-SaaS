
#  PROJETO DETECTIVE — main.py
#  Responsabilidade: Orquestrar todos os módulos em sequência.
#  Dois modos de uso:
#
#  1. MANUAL — coleta uma vez e exibe os alertas:
#     python main.py
#
#  2. AUTOMÁTICO — monitora continuamente
#     python main.py --auto
#     python main.py --auto --intervalo 4   (a cada 4 horas)
#
#  3. DASHBOARD — abre a interface visual:


import argparse
import time
import os
from datetime import datetime

from coletor   import buscar_pagina
from extrator  import extrair_dados
from historico import salvar_historico, resumo_historico
from alertas   import verificar_alertas, exibir_alertas

INTERVALO_PADRAO_HORAS = 3


def rodar_detective(modo_visivel=True):  
    """
    Executa o ciclo completo do DETECTIVE:
    1. Coleta o HTML (coletor.py)
    2. Extrai os dados (extrator.py)
    3. Salva no histórico (historico.py)
    4. Verifica e exibe alertas (alertas.py)
    """

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"   DETECTIVE — Iniciando ciclo")
    print(f"   {agora}")
    print(f"{'='*55}\n")

    print("── PASSO 1/4: Coletando HTML do concorrente...")
    html = buscar_pagina(modo_visivel=modo_visivel)

    if not html:
        print("[MAIN] ❌ Falha na coleta. Abortando ciclo.")
        return None

    print("\n── PASSO 2/4: Extraindo dados com BeautifulSoup...")
    dados = extrair_dados(html)

    if not dados:
        print("[MAIN] ❌ Falha na extração. Abortando ciclo.")
        return None

    print("\n── PASSO 3/4: Salvando no histórico CSV...")
    salvar_historico(dados)

    print("\n── PASSO 4/4: Verificando alertas...")
    alertas = verificar_alertas(dados)
    exibir_alertas(alertas)

    resumo = resumo_historico()
    if resumo:
        print(f"\n Total de coletas: {resumo['total_registros']}")
        print(f"   Preço mín: R$ {resumo['preco_minimo']:.2f} | Máx: R$ {resumo['preco_maximo']:.2f}")

    print(f"\n Ciclo concluído em {datetime.now().strftime('%H:%M:%S')}")
    return alertas


def modo_automatico(intervalo_horas=INTERVALO_PADRAO_HORAS):
    """
    Roda o DETECTIVE continuamente de X em X horas.
    Pressione Ctrl+C para parar.
    """

    intervalo_segundos = intervalo_horas * 3600

    print(f"\n{'='*55}")
    print(f"   DETECTIVE — MODO AUTOMÁTICO ATIVADO")
    print(f"    Monitorando a cada {intervalo_horas}h")
    print(f"    Pressione Ctrl+C para parar")
    print(f"{'='*55}\n")

    ciclo = 1

    while True:
        print(f"\n🔄 Ciclo #{ciclo}")
        rodar_detective(modo_visivel=True)  # ← sempre visível

        proxima_str = datetime.now().strftime("%H:%M")
        print(f"\n⏳ Próxima coleta em {intervalo_horas}h")
        print(f"   Aguardando... (Ctrl+C para parar)\n")

        ciclo += 1

        try:
            time.sleep(intervalo_segundos)
        except KeyboardInterrupt:
            print("\n\n DETECTIVE pausado pelo usuário.")
            print("   Até a próxima! 🕵️")
            break


def abrir_dashboard():
    print("\n  Abrindo DETECTIVE Dashboard...")
    print("   Acesse: http://localhost:8501\n")
    os.system("streamlit run dashboard.py")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="  DETECTIVE — Monitoramento de concorrente no Mercado Livre"
    )
    parser.add_argument("--auto",      action="store_true", help="Modo automático")
    parser.add_argument("--intervalo", type=float, default=INTERVALO_PADRAO_HORAS)
    parser.add_argument("--dashboard", action="store_true", help="Abre o dashboard")

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════╗
║         🕵️   DETECTIVE v1.0                          ║
║         Inteligência Competitiva — Mercado Livre     ║
║         "Se ele respirar, saberemos."               ║
╚══════════════════════════════════════════════════════╝
    """)

    if args.dashboard:
        abrir_dashboard()
    elif args.auto:
        modo_automatico(intervalo_horas=args.intervalo)
    else:
        rodar_detective(modo_visivel=True)  # ← sempre visível