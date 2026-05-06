"""Tela Por Município — cobertura geográfica."""
import streamlit as st
import pandas as pd
from lib.auth import check_password, logout_button
from lib import db

st.set_page_config(page_title="Por Município", page_icon="🗺️", layout="wide")
if not check_password(): st.stop()
logout_button()

st.title("🗺️ Cobertura por Município")

stats = db.stats_municipios()
df = pd.DataFrame(stats)

if df.empty:
    st.info("Nenhum município cadastrado.")
    st.stop()

# Resumo
n_sem = (df["Risco"] == "SEM COBERTURA").sum()
n_baixo = (df["Risco"] == "BAIXO").sum()
n_ok = (df["Risco"] == "OK").sum()

a, b, c, d = st.columns(4)
a.metric("Total", len(df))
b.metric("🔴 Sem cobertura", n_sem)
c.metric("🟡 Cobertura baixa", n_baixo)
d.metric("🟢 OK", n_ok)

st.divider()

# Filtro
risco_filtro = st.selectbox("Filtrar por risco", ["Todos", "SEM COBERTURA", "BAIXO", "OK"])
df_view = df.copy() if risco_filtro == "Todos" else df[df["Risco"] == risco_filtro]

st.dataframe(df_view, use_container_width=True, hide_index=True, height=500)

st.divider()

# Drill-down por município
st.subheader("👥 Pesquisadores por município")
muni_sel = st.selectbox("Selecione o município", df["Município"].tolist())
pesqs = db.listar_pesquisadores({"municipio": muni_sel})

if pesqs:
    rows = [{
        "Nome": p["nome"],
        "Telefone": p.get("telefone") or "",
        "Aprovação": p.get("aprovacao") or "",
        "No grupo": p.get("status_grupo") or "",
        "Decisão": p.get("decisao_atual") or "",
        "Audit. pendente": "Sim" if p.get("audit_pendente") else "Não",
    } for p in pesqs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.warning(f"Nenhum pesquisador cadastrado em {muni_sel}.")
