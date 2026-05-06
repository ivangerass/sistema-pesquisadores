"""Tela de Pesquisadores — CRUD com filtros."""
import streamlit as st
import pandas as pd
from lib.auth import check_password, logout_button
from lib import db
from lib.const import APROVACAO, STATUS_GRUPO, DECISOES

st.set_page_config(page_title="Pesquisadores", page_icon="👥", layout="wide")
if not check_password(): st.stop()
logout_button()

st.title("👥 Pesquisadores")

# ===== FILTROS =====
with st.expander("🔍 Filtros", expanded=True):
    f1, f2, f3 = st.columns(3)
    munis = sorted({m["nome"] for m in db.listar_municipios()})
    f_muni = f1.selectbox("Município", ["Todos"] + munis)
    f_aprov = f2.selectbox("Aprovação", ["Todos"] + APROVACAO)
    f_dec = f3.selectbox("Decisão atual", ["Todos"] + DECISOES)

filtros = {}
if f_muni != "Todos": filtros["municipio"] = f_muni
if f_aprov != "Todos": filtros["aprovacao"] = f_aprov
if f_dec != "Todos": filtros["decisao_atual"] = f_dec

pesqs = db.listar_pesquisadores(filtros)
st.caption(f"{len(pesqs)} pesquisador(es) encontrados.")

# ===== TABELA =====
if pesqs:
    df = pd.DataFrame(pesqs)[[
        "id", "nome", "municipio", "telefone", "aprovacao",
        "status_grupo", "decisao_atual", "audit_pendente", "proxima_acao"
    ]]
    df.columns = ["ID", "Nome", "Município", "Telefone", "Aprovação",
                  "No grupo", "Decisão", "Audit. pendente", "Próxima ação"]
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)
else:
    st.info("Nenhum pesquisador encontrado com esses filtros.")

st.divider()

# ===== AÇÕES =====
tab1, tab2, tab3 = st.tabs(["✏️ Editar", "➕ Novo", "🗑️ Remover"])

# --- EDITAR ---
with tab1:
    if not pesqs:
        st.info("Sem pesquisadores para editar.")
    else:
        opcoes = {f"{p['nome']} ({p['municipio']})": p["id"] for p in pesqs}
        sel = st.selectbox("Selecione", list(opcoes.keys()), key="edit_sel")
        pid = opcoes[sel]
        p = db.get_pesquisador(pid)

        with st.form("form_editar"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome", p["nome"])
            municipio = c2.selectbox("Município", munis, index=munis.index(p["municipio"]) if p["municipio"] in munis else 0)
            telefone = c1.text_input("Telefone", p.get("telefone") or "")
            cpf = c2.text_input("CPF", p.get("cpf") or "")
            email = c1.text_input("Email", p.get("email") or "")
            pix = c2.text_input("Chave Pix", p.get("pix") or "")

            c3, c4 = st.columns(2)
            aprovacao = c3.selectbox("Aprovação", APROVACAO,
                index=APROVACAO.index(p["aprovacao"]) if p["aprovacao"] in APROVACAO else 0)
            status_grupo = c4.selectbox("Status no grupo", STATUS_GRUPO,
                index=STATUS_GRUPO.index(p["status_grupo"]) if p.get("status_grupo") in STATUS_GRUPO else 0)
            decisao = c3.selectbox("Decisão atual", DECISOES,
                index=DECISOES.index(p["decisao_atual"]) if p.get("decisao_atual") in DECISOES else 0)
            audit_pend = c4.checkbox("Auditoria pendente", p.get("audit_pendente", False))

            proxima = st.text_area("Próxima ação", p.get("proxima_acao") or "", height=68)
            obs = st.text_area("Observações", p.get("observacoes") or "", height=68)

            if st.form_submit_button("Salvar", type="primary"):
                db.atualizar_pesquisador(pid, {
                    "nome": nome, "municipio": municipio, "telefone": telefone,
                    "cpf": cpf, "email": email, "pix": pix,
                    "aprovacao": aprovacao, "status_grupo": status_grupo,
                    "decisao_atual": decisao, "audit_pendente": audit_pend,
                    "proxima_acao": proxima, "observacoes": obs,
                })
                st.success("Pesquisador atualizado.")
                st.rerun()

# --- NOVO ---
with tab2:
    with st.form("form_novo"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome*")
        municipio = c2.selectbox("Município*", munis if munis else ["—"])
        telefone = c1.text_input("Telefone")
        cpf = c2.text_input("CPF")
        email = c1.text_input("Email")
        pix = c2.text_input("Chave Pix")

        c3, c4 = st.columns(2)
        aprovacao = c3.selectbox("Aprovação", APROVACAO, index=0)
        status_grupo = c4.selectbox("Status no grupo", STATUS_GRUPO, index=2)  # A ADICIONAR
        decisao = c3.selectbox("Decisão atual", DECISOES, index=8)  # PENDENTE

        if st.form_submit_button("Cadastrar", type="primary"):
            if nome and municipio:
                db.criar_pesquisador({
                    "nome": nome, "municipio": municipio, "telefone": telefone,
                    "cpf": cpf, "email": email, "pix": pix,
                    "aprovacao": aprovacao, "status_grupo": status_grupo,
                    "decisao_atual": decisao,
                })
                st.success(f"Pesquisador '{nome}' cadastrado.")
                st.rerun()
            else:
                st.error("Nome e município são obrigatórios.")

# --- REMOVER ---
with tab3:
    if not pesqs:
        st.info("Sem pesquisadores para remover.")
    else:
        opcoes_rm = {f"{p['nome']} ({p['municipio']})": p["id"] for p in pesqs}
        sel_rm = st.selectbox("Selecione", list(opcoes_rm.keys()), key="rm_sel")
        st.warning("Remover é permanente. Auditorias e pagamentos vinculados também serão removidos.")
        if st.button("Confirmar remoção", type="secondary"):
            db.deletar_pesquisador(opcoes_rm[sel_rm])
            st.success("Removido.")
            st.rerun()
