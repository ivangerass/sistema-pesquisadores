"""Dashboard executivo com KPIs."""
import streamlit as st
import pandas as pd
from lib.auth import check_password, logout_button
from lib import db
from lib.const import cor_risco

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
if not check_password(): st.stop()
logout_button()

st.title("📊 Dashboard")
st.caption("Atualiza automaticamente a partir das outras telas.")

# ===== KPIs =====
stats = db.stats_geral()

c1, c2, c3 = st.columns(3)
c1.metric("Pesquisadores ativos", stats["total"])
c2.metric("Aprovados", stats["aprovados"])
c3.metric("Reservas", stats["reservas"])

c4, c5, c6 = st.columns(3)
c4.metric("Em advertência final", stats["advert_final"], delta=None, delta_color="off")
c5.metric("Auditoria pendente", stats["audit_pendente"], delta=None, delta_color="off")
c6.metric("Eliminados", stats["eliminados"], delta=None, delta_color="off")

st.divider()

# ===== Cobertura =====
st.subheader("🗺️ Cobertura por município")

munis = db.stats_municipios()
df = pd.DataFrame(munis)

if not df.empty:
    n_sem = (df["Risco"] == "SEM COBERTURA").sum()
    n_baixo = (df["Risco"] == "BAIXO").sum()
    n_ok = (df["Risco"] == "OK").sum()

    a, b, c = st.columns(3)
    a.metric("🔴 Sem cobertura", n_sem)
    b.metric("🟡 Cobertura baixa", n_baixo)
    c.metric("🟢 OK", n_ok)

    # Filtro
    risco_filtro = st.selectbox("Filtrar por risco", ["Todos", "SEM COBERTURA", "BAIXO", "OK"])
    if risco_filtro != "Todos":
        df = df[df["Risco"] == risco_filtro]

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum município cadastrado ainda.")

st.divider()

# ===== Pagamentos R1 =====
st.subheader("💰 Pagamentos — R1")

pagtos = db.listar_pagamentos(rodada="R1")
if pagtos:
    df_pag = pd.DataFrame(pagtos)
    
    total = df_pag["valor_total"].sum()
    pagos = (df_pag["status"] == "PAGO").sum()
    liberados = (df_pag["status"] == "LIBERADO").sum()
    bloqueados = (df_pag["status"].str.contains("BLOQUEADO", na=False)).sum()
    
    a, b, c, d = st.columns(4)
    a.metric("Total a pagar (R1)", f"R$ {total:,.2f}".replace(",", "."))
    b.metric("Liberados", liberados)
    c.metric("Pagos", pagos)
    d.metric("Bloqueados", bloqueados)
else:
    st.info("Nenhum pagamento R1 cadastrado ainda.")

st.divider()

# ===== Próximas ações =====
st.subheader("📋 Próximas ações sugeridas")

acoes = []
if stats["audit_pendente"] > 0:
    acoes.append(f"⚠️ {stats['audit_pendente']} pesquisador(es) com auditoria pendente — concluir antes de liberar pagamento.")
if stats["advert_final"] > 0:
    acoes.append(f"🔴 {stats['advert_final']} em advertência final — agendar retreinamento individual.")

if not df.empty:
    if (df["Risco"] == "SEM COBERTURA").any() if risco_filtro == "Todos" else False:
        munis_sem = df[df["Risco"] == "SEM COBERTURA"]["Município"].tolist()
        if munis_sem:
            acoes.append(f"🔴 Municípios sem cobertura: {', '.join(munis_sem[:3])}{'...' if len(munis_sem)>3 else ''}")

if acoes:
    for a in acoes:
        st.markdown(f"- {a}")
else:
    st.success("Nenhuma ação crítica pendente.")
