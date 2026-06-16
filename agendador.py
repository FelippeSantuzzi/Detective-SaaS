# ============================================================
#  PROJETO DETECTIVE — agendador.py
#  Responsabilidade: rodar o DETECTIVE automaticamente
#  de X em X horas, sem precisar de cron ou configuração.
#
#  Como usar:
#    python agendador.py              (a cada 3 horas)
#    python agendador.py --intervalo 2  (a cada 2 horas)
#
#  Para parar: Ctrl+C
# ============================================================

import time
import argparse
from datetime import datetime, timedelta
from main import rodar_detective

INTERVALO_PADRAO = 3  # horas


def agendador(intervalo_horas=INTERVALO_PADRAO):

    intervalo_segundos = intervalo_horas * 3600

    print("""
╔══════════════════════════════════════════════════════╗
║         🕵️   DETECTIVE — AGENDADOR                   ║
║         Monitoramento automático ativado             ║
╚══════════════════════════════════════════════════════╝
    """)

    print(f"⏱️  Intervalo: a cada {intervalo_horas} hora(s)")
    print(f"🛑  Para parar: Ctrl+C")
    print(f"📋  Log salvo em: detective.log")
    print()

    ciclo = 1

    while True:
        agora = datetime.now()
        proxima = agora + timedelta(hours=intervalo_horas)

        print(f"\n{'='*55}")
        print(f"🔄 Ciclo #{ciclo} — {agora.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*55}")

        try:
            rodar_detective(modo_visivel=True)
        except Exception as e:
            print(f"[AGENDADOR] ❌ Erro no ciclo: {e}")

        print(f"\n⏳ Próxima coleta: {proxima.strftime('%d/%m/%Y às %H:%M')}")
        print(f"   Aguardando {intervalo_horas}h... (Ctrl+C para parar)")

        ciclo += 1

        try:
            time.sleep(intervalo_segundos)
        except KeyboardInterrupt:
            print("\n\n🛑 Agendador parado pelo usuário.")
            print("   DETECTIVE offline. Até a próxima! 🕵️")
            break


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--intervalo",
        type=float,
        default=INTERVALO_PADRAO,
        help=f"Intervalo em horas (padrão: {INTERVALO_PADRAO})"
    )
    args = parser.parse_args()

    agendador(intervalo_horas=args.intervalo)