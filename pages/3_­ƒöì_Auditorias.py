"""Tela de Auditorias — histórico por rodada."""
import streamlit as st
import pandas as pd
from datetime import date
from lib.auth import check_password, logout_button
from lib import db
from lib.const import RODADAS, DECISOES

st.set_page_config(page_title="Auditorias", page_icon="🔍", layout="wide")
if not check_password(): st.stop()
logout_button()

st.title("🔍 Auditorias")

# ===== FILTRO =====
f_rodada = st.selectbox("Rodada", ["Todas"] + RODADAS)
auds = db.listar_auditorias(rodada=f_rodada)

st.caption(f"{len(auds)} auditoria(s).")

# ===== TABELA =====
if auds:
    rows = []
    for a in auds:
        pesq = a.get("pesquisadores") or {}
        rows.append({
            "ID": a["id"],
            "Rodada": a["rodada"],
            "Data": a.get("data_auditoria"),
            "Pesquisador": pesq.get("nome", ""),
            "Município": pesq.get("municipio", ""),
            "Auditor": a.get("auditor"),
            "Pesq. auditadas": a.get("pesquisas_auditadas"),
            "Resultado": a.get("resultado"),
            "Mensagem enviada": "Sim" if a.get("mensagem_enviada") else "Não",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=350)
else:
    st.info("Nenhuma auditoria nesta rodada.")

st.divider()

# ===== AÇÕES =====
tab1, tab2 = st.tabs(["➕ Nova auditoria", "✏️ Editar / Remover"])

pesqs = db.listar_pesquisadores()

# --- NOVA ---
with tab1:
    with st.form("form_nova_audit"):
        c1, c2 = st.columns(2)

        opcoes = {f"{p['nome']} ({p['municipio']})": p["id"] for p in pesqs}
        sel = c1.selectbox("Pesquisador*", list(opcoes.keys()) if opcoes else ["—"])
        rodada = c2.selectbox("Rodada*", RODADAS, index=0)

        data_aud = c1.date_input("Data da auditoria", value=date.today())
        auditor = c2.text_input("Auditor")

        c3, c4 = st.columns(2)
        pesq_qtde = c3.number_input("Pesquisas auditadas", min_value=0, value=0, step=1)
        resultado = c4.selectbox("Resultado*", DECISOES, index=0)

        detalhes = st.text_area("Detalhes / pontos a corrigir", height=100)
        msg_enviada = st.checkbox("Mensagem WhatsApp já foi enviada")

        if st.form_submit_button("Registrar auditoria", type="primary"):
            if opcoes:
                db.criar_auditoria({
                    "pesquisador_id": opcoes[sel],
                    "rodada": rodada,
                    "data_auditoria": data_aud.isoformat(),
                    "auditor": auditor,
                    "pesquisas_auditadas": pesq_qtde or None,
                    "resultado": resultado,
                    "detalhes": detalhes,
                    "mensagem_enviada": msg_enviada,
                })
                # Atualiza decisao_atual do pesquisador
                db.atualizar_pesquisador(opcoes[sel], {
                    "decisao_atual": resultado,
                    "audit_pendente": resultado == "AUDITORIA PENDENTE",
                })
                st.success("Auditoria registrada e decisão do pesquisador atualizada.")
                st.rerun()

# --- EDITAR / REMOVER ---
with tab2:
    if not auds:
        st.info("Sem auditorias para editar.")
    else:
        opcoes_a = {
            f"{a['rodada']} • {(a.get('pesquisadores') or {}).get('nome','?')} • {a.get('data_auditoria','')}": a["id"]
            for a in auds
        }
        sel_a = st.selectbox("Selecione a auditoria", list(opcoes_a.keys()), key="edit_aud")
        aid = opcoes_a[sel_a]
        a = next(x for x in auds if x["id"] == aid)

        with st.form("form_edit_audit"):
            c1, c2 = st.columns(2)
            auditor = c1.text_input("Auditor", a.get("auditor") or "")
            pesq_qtde = c2.number_input("Pesquisas auditadas",
                min_value=0, value=a.get("pesquisas_auditadas") or 0, step=1)
            resultado = c1.selectbox("Resultado", DECISOES,
                index=DECISOES.index(a["resultado"]) if a.get("resultado") in DECISOES else 0)
            msg_enviada = c2.checkbox("Mensagem enviada", a.get("mensagem_enviada", False))
            detalhes = st.text_area("Detalhes", a.get("detalhes") or "", height=120)

            col_save, col_del = st.columns(2)
            if col_save.form_submit_button("Salvar alterações", type="primary"):
                db.atualizar_auditoria(aid, {
                    "auditor": auditor, "pesquisas_auditadas": pesq_qtde or None,
                    "resultado": resultado, "detalhes": detalhes,
                    "mensagem_enviada": msg_enviada,
                })
                st.success("Auditoria atualizada.")
                st.rerun()
            if col_del.form_submit_button("🗑️ Remover", type="secondary"):
                db.deletar_auditoria(aid)
                st.success("Auditoria removida.")
                st.rerun()
