"""Tela de Pagamentos — controle financeiro por rodada."""
import streamlit as st
import pandas as pd
from datetime import date
from lib.auth import check_password, logout_button
from lib import db
from lib.const import RODADAS, STATUS_PAGAMENTO

st.set_page_config(page_title="Pagamentos", page_icon="💰", layout="wide")
if not check_password(): st.stop()
logout_button()

st.title("💰 Pagamentos")
st.caption("Bloqueio sugerido para pesquisadores com auditoria pendente.")

f_rodada = st.selectbox("Rodada", ["Todas"] + RODADAS, index=1)
pagtos = db.listar_pagamentos(rodada=f_rodada)

if pagtos:
    rows = []
    for p in pagtos:
        pesq = p.get("pesquisadores") or {}
        rows.append({
            "ID": p["id"],
            "Rodada": p["rodada"],
            "Pesquisador": pesq.get("nome", ""),
            "Município": pesq.get("municipio", ""),
            "Pix": pesq.get("pix") or "",
            "Pesq.": p.get("pesquisas_realizadas", 0),
            "Valor un.": float(p.get("valor_unitario") or 5.0),
            "Total": float(p.get("valor_total") or 0),
            "Status": p.get("status", ""),
            "Data pgto": p.get("data_pagamento") or "",
        })
    df = pd.DataFrame(rows)

    # Totais
    total_geral = df["Total"].sum()
    pagos = (df["Status"] == "PAGO").sum()
    liberados = (df["Status"] == "LIBERADO").sum()
    bloqueados = (df["Status"].str.contains("BLOQUEADO", na=False)).sum()
    suspensos = (df["Status"] == "SUSPENSO").sum()

    a, b, c, d, e = st.columns(5)
    a.metric("Total", f"R$ {total_geral:,.2f}".replace(",","."))
    b.metric("Liberados", liberados)
    c.metric("Pagos", pagos)
    d.metric("Bloqueados", bloqueados)
    e.metric("Suspensos", suspensos)

    st.dataframe(
        df, use_container_width=True, hide_index=True, height=380,
        column_config={
            "Valor un.": st.column_config.NumberColumn(format="R$ %.2f"),
            "Total": st.column_config.NumberColumn(format="R$ %.2f"),
        },
    )
else:
    st.info("Nenhum pagamento cadastrado nessa rodada.")

st.divider()

# ===== AÇÕES =====
tab1, tab2 = st.tabs(["✏️ Atualizar status / data", "➕ Lançar pagamento"])

with tab1:
    if not pagtos:
        st.info("Nada para atualizar.")
    else:
        opcoes = {f"{(p.get('pesquisadores') or {}).get('nome','?')} • {p['rodada']}": p["id"] for p in pagtos}
        sel = st.selectbox("Selecione", list(opcoes.keys()), key="pag_edit")
        pid = opcoes[sel]
        p = next(x for x in pagtos if x["id"] == pid)

        with st.form("form_pag"):
            c1, c2 = st.columns(2)
            status = c1.selectbox("Status", STATUS_PAGAMENTO,
                index=STATUS_PAGAMENTO.index(p["status"]) if p.get("status") in STATUS_PAGAMENTO else 0)
            data_pg = c2.date_input("Data do pagamento",
                value=date.fromisoformat(p["data_pagamento"]) if p.get("data_pagamento") else None)
            qtd = c1.number_input("Pesquisas realizadas",
                min_value=0, value=p.get("pesquisas_realizadas", 0), step=1)
            valor_un = c2.number_input("Valor unitário (R$)",
                min_value=0.0, value=float(p.get("valor_unitario") or 5.0), step=0.50, format="%.2f")
            obs = st.text_area("Observação", p.get("observacao") or "", height=68)

            if st.form_submit_button("Salvar", type="primary"):
                db.atualizar_pagamento(pid, {
                    "status": status,
                    "data_pagamento": data_pg.isoformat() if data_pg else None,
                    "pesquisas_realizadas": qtd,
                    "valor_unitario": valor_un,
                    "observacao": obs,
                })
                st.success("Pagamento atualizado.")
                st.rerun()

with tab2:
    pesqs = db.listar_pesquisadores()
    with st.form("form_novo_pag"):
        c1, c2 = st.columns(2)
        opcoes = {f"{p['nome']} ({p['municipio']})": p["id"] for p in pesqs}
        sel = c1.selectbox("Pesquisador*", list(opcoes.keys()) if opcoes else ["—"])
        rodada = c2.selectbox("Rodada*", RODADAS)
        qtd = c1.number_input("Pesquisas realizadas", min_value=0, value=0, step=1)
        valor_un = c2.number_input("Valor unitário (R$)", min_value=0.0, value=5.0, step=0.50, format="%.2f")
        status = c1.selectbox("Status", STATUS_PAGAMENTO, index=0)

        if st.form_submit_button("Lançar", type="primary"):
            if opcoes:
                try:
                    db.criar_pagamento({
                        "pesquisador_id": opcoes[sel],
                        "rodada": rodada,
                        "pesquisas_realizadas": qtd,
                        "valor_unitario": valor_un,
                        "status": status,
                    })
                    st.success("Pagamento lançado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}. Pode já existir pagamento dessa rodada para esse pesquisador.")
