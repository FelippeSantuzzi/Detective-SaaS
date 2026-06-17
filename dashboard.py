#  PROJETO DETECTIVE — dashboard.py
#  Responsabilidade: exibir todos os dados numa interface
#  visual interativa usando Streamlit.
#
#  Biblioteca usada: Streamlit
#
#  Como rodar:
#    streamlit run dashboard.py
#
#  O dashboard exibe:
#    - Campo para colar link do concorrente
#    - Dossier atual do concorrente
#    - Alertas inteligentes em tempo real
#    - Gráfico histórico de preços
#    - Histórico de estoque
#    - Tabela completa de registros

import streamlit as st
import pandas as pd
from datetime import datetime
import re

from historico import salvar_historico, carregar_historico, resumo_historico
from alertas   import verificar_alertas
from api_ml    import coletar_por_link


# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="DETECTIVE 🕵️",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .block-container { padding-top: 1.5rem; }

    .detective-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #f5c842;
        border-radius: 12px;
        padding: 20px 30px;
        margin-bottom: 20px;
    }
    .detective-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #f5c842;
        letter-spacing: 4px;
        margin: 0;
    }
    .detective-subtitle {
        color: #888899;
        font-size: 0.95rem;
        margin-top: 4px;
    }

    .monitorar-box {
        background: #1e1e2e;
        border: 1px solid #f5c842;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }

    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #f5c842;
        margin-bottom: 10px;
    }
    .metric-label {
        color: #888899;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
    }

    .alerta-critico  { background:#2d1a1a; border-left:4px solid #e63946; border-radius:8px; padding:14px 18px; margin:8px 0; }
    .alerta-atencao  { background:#2d2a1a; border-left:4px solid #f5c842; border-radius:8px; padding:14px 18px; margin:8px 0; }
    .alerta-positivo { background:#1a2d1a; border-left:4px solid #2dc653; border-radius:8px; padding:14px 18px; margin:8px 0; }
    .alerta-info     { background:#1a1e2d; border-left:4px solid #3a86ff; border-radius:8px; padding:14px 18px; margin:8px 0; }

    .alerta-titulo  { font-weight:700; font-size:1rem; color:#ffffff; }
    .alerta-msg     { color:#cccccc; font-size:0.88rem; margin-top:4px; }
    .alerta-acao    { color:#f5c842; font-size:0.85rem; margin-top:6px; font-style:italic; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────

def safe_float(valor, padrao=0.0):
    """Converte para float com segurança — evita erros com URLs ou textos."""
    try:
        return float(valor)
    except (ValueError, TypeError):
        return padrao

def safe_int(valor, padrao=0):
    """Converte para int com segurança."""
    try:
        return int(valor)
    except (ValueError, TypeError):
        return padrao


# ─────────────────────────────────────────────────────────────
# CARREGA DADOS — precisa vir antes da sidebar
# ─────────────────────────────────────────────────────────────

historico = carregar_historico()

if historico:
    dados_atuais = historico[-1]
else:
    dados_atuais = None


# ─────────────────────────────────────────────────────────────
# SIDEBAR — Controles
# ─────────────────────────────────────────────────────────────

with st.sidebar:

    # Imagem dinâmica — puxada do último registro do histórico
    img_url = dados_atuais.get("imagem", "") if dados_atuais else ""
    if img_url and img_url.startswith("http"):
        st.image(img_url, width=200)

    st.markdown("### ⚙️ Controles")

    # Link dinâmico — sempre aponta para o anúncio monitorado
    st.markdown("**Anúncio monitorado:**")
    link_anuncio = dados_atuais.get("link", "") if dados_atuais else ""
    if link_anuncio:
        st.markdown(f"[Abrir no Mercado Livre]({link_anuncio})")
    else:
        st.caption("Nenhum anúncio monitorado ainda.")

    st.markdown("---")

    # Botão de atualização manual
    if st.button("🔄 Atualizar agora", use_container_width=True, type="primary"):
        if link_anuncio:
            with st.spinner("🕵️ DETECTIVE em ação..."):
                dados = coletar_por_link(link_anuncio)
                if dados:
                    salvar_historico(dados)
                    st.success("✅ Dados atualizados!")
                    st.rerun()
                else:
                    st.error("❌ Falha na coleta.")
        else:
            st.warning("Cole um link primeiro.")

    st.markdown("---")
    st.markdown("### 📊 Resumo")
    resumo = resumo_historico()
    if resumo:
        st.metric("Total de coletas", resumo["total_registros"])
        if resumo["preco_minimo"]:
            st.metric("Preço mínimo", f"R$ {resumo['preco_minimo']:.2f}")
        if resumo["preco_maximo"]:
            st.metric("Preço máximo", f"R$ {resumo['preco_maximo']:.2f}")
        st.caption(f"Primeira coleta: {resumo['primeira_coleta']}")
        st.caption(f"Última coleta: {resumo['ultima_coleta']}")

    st.markdown("---")
    st.caption("DETECTIVE v1.0 • 2026")


# ─────────────────────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────────────────────

col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("detective_logo.png", width=200)
with col_titulo:
    st.markdown("""
    <div class="detective-header">
        <div class="detective-title">DETECTIVE</div>
        <div class="detective-subtitle">
            Inteligência Competitiva em tempo real • Mercado Livre
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# BLOCO 0 — CAMPO PARA MONITORAR NOVO LINK
# ─────────────────────────────────────────────────────────────

st.markdown("### 🎯 Monitorar Concorrente")

col_input, col_btn = st.columns([4, 1])

with col_input:
    link_novo = st.text_input(
        label="Cole o link do anúncio do Mercado Livre:",
        placeholder="https://www.mercadolivre.com.br/...",
        label_visibility="collapsed",
    )

with col_btn:
    monitorar = st.button("🔍 Monitorar", use_container_width=True, type="primary")

if monitorar:
    if not link_novo or not link_novo.startswith("http"):
        st.error("❌ Cole um link válido do Mercado Livre.")
    else:
        with st.spinner("🔍 DETECTIVE consultando API do Mercado Livre..."):
            dados = coletar_por_link(link_novo)

        if dados:
            salvar_historico(dados)
            st.success(f"✅ Dados coletados! {dados.get('titulo', '')} — R$ {dados.get('preco', '')}")
            st.rerun()
        else:
            st.error("❌ Não foi possível encontrar esse anúncio. Verifique o link e tente novamente.")

st.markdown("---")


# ─────────────────────────────────────────────────────────────
# BLOCO 1 — DOSSIER ATUAL (métricas principais)
# ─────────────────────────────────────────────────────────────

st.markdown("### 📋 Dossier do Concorrente")

if dados_atuais:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        preco = safe_float(dados_atuais.get("preco", 0))
        delta = None
        if len(historico) >= 2:
            preco_ant = safe_float(historico[-2].get("preco", preco))
            delta = f"R$ {preco - preco_ant:+.2f}"
        st.metric("💰 Preço Atual", f"R$ {preco:.2f}", delta=delta)

    with col2:
        desconto = dados_atuais.get("desconto", "Sem desconto")
        st.metric("🔖 Desconto", desconto)

    with col3:
        frete = dados_atuais.get("frete_gratis", "False")
        frete_ok = str(frete).lower() in ["true", "1", "sim"]
        st.metric("🚚 Frete Grátis", "✅ SIM" if frete_ok else "❌ NÃO")

    with col4:
        estoque = dados_atuais.get("estoque", "?")
        delta_est = None
        if len(historico) >= 2:
            est_ant = historico[-2].get("estoque", "")
            try:
                delta_est = f"{int(estoque) - int(est_ant):+d} un."
            except:
                pass
        st.metric("📦 Estoque", f"{estoque} un.", delta=delta_est, delta_color="inverse")

    with col5:
        aval = safe_int(dados_atuais.get("avaliacoes", 0))
        delta_aval = None
        if len(historico) >= 2:
            aval_ant = safe_int(historico[-2].get("avaliacoes", aval))
            diff = aval - aval_ant
            if diff != 0:
                delta_aval = f"+{diff} novas"
        st.metric("⭐ Avaliações", aval, delta=delta_aval)

    st.caption(f"📦 {dados_atuais.get('titulo', '')}  |  🏆 {dados_atuais.get('vendas', '')}  |  🕐 Última coleta: {dados_atuais.get('data_hora', '')}")

else:
    st.warning("⚠️ Nenhum dado disponível. Cole um link acima e clique em Monitorar.")


# ─────────────────────────────────────────────────────────────
# BLOCO 2 — ALERTAS
# ─────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 🚨 Central de Alertas")

if dados_atuais:
    dados_conv = dict(dados_atuais)
    try:
        dados_conv["preco"]      = safe_float(dados_atuais.get("preco", 0))
        dados_conv["avaliacoes"] = safe_int(dados_atuais.get("avaliacoes", 0))
        dados_conv["estoque"]    = safe_int(dados_atuais.get("estoque", 0)) if dados_atuais.get("estoque") else None
    except:
        pass

    alertas = verificar_alertas(dados_conv)

    for alerta in alertas:
        nivel = alerta.get("nivel", "info")
        st.markdown(f"""
        <div class="alerta-{nivel}">
            <div class="alerta-titulo">{alerta['emoji']} {alerta['titulo']}</div>
            <div class="alerta-msg">📋 {alerta['mensagem']}</div>
            <div class="alerta-acao">⚡ {alerta['acao']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhum dado para analisar ainda.")


# ─────────────────────────────────────────────────────────────
# BLOCO 3 — GRÁFICOS
# ─────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 📈 Histórico Visual")

if len(historico) >= 2:
    df = pd.DataFrame(historico)

    df["preco"]      = pd.to_numeric(df["preco"], errors="coerce")
    df["estoque"]    = pd.to_numeric(df["estoque"], errors="coerce")
    df["avaliacoes"] = pd.to_numeric(df["avaliacoes"], errors="coerce")
    df["data_hora"]  = pd.to_datetime(df["data_hora"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df = df.sort_values("data_hora")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**💰 Evolução do Preço**")
        st.line_chart(df.set_index("data_hora")["preco"], color="#f5c842", height=250)

    with col_g2:
        st.markdown("**📦 Evolução do Estoque**")
        st.line_chart(df.set_index("data_hora")["estoque"], color="#e63946", height=250)

else:
    st.info("📊 Acumule pelo menos 2 coletas para ver os gráficos de evolução.")
    st.caption("Cole um link acima e clique em Monitorar algumas vezes ao longo do dia.")


# ─────────────────────────────────────────────────────────────
# BLOCO 4 — TABELA HISTÓRICA
# ─────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 📂 Tabela de Registros")

if historico:
    df_tabela = pd.DataFrame(historico)

    df_tabela = df_tabela.rename(columns={
        "data_hora"    : "Data/Hora",
        "preco"        : "Preço (R$)",
        "desconto"     : "Desconto",
        "frete_gratis" : "Frete Grátis",
        "estoque"      : "Estoque (un.)",
        "avaliacoes"   : "Avaliações",
        "vendas"       : "Vendas",
    })

    colunas_exibir = ["Data/Hora", "Preço (R$)", "Desconto", "Frete Grátis", "Estoque (un.)", "Avaliações", "Vendas"]
    colunas_exibir = [c for c in colunas_exibir if c in df_tabela.columns]

    st.dataframe(
        df_tabela[colunas_exibir].sort_values("Data/Hora", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = df_tabela.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Baixar histórico completo (CSV)",
        data=csv_data,
        file_name=f"detective_historico_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("Nenhum registro no histórico ainda.")