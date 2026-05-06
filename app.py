"""
Sistema de Controle de Pesquisadores — Perspectiva 2026
App principal (entry point com login).
"""
import streamlit as st
from lib.auth import check_password, logout_button

st.set_page_config(
    page_title="Pesquisadores Perspectiva 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS minimalista
st.markdown("""
<style>
    .stApp { background-color: #fafafa; }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 4px;
    }
    .stDataFrame { border: 1px solid #e0e0e0; }
    h1, h2, h3 { color: #404040; }
</style>
""", unsafe_allow_html=True)

if not check_password():
    st.stop()

logout_button()

st.title("📊 Sistema de Pesquisadores — Perspectiva 2026")
st.caption("Operação Interior do Amazonas — 61 municípios")

st.markdown("""
### Bem-vindo

Use o menu lateral para navegar entre as seções:

- **Dashboard** — visão geral do quadro com KPIs e alertas.
- **Pesquisadores** — base mestra (cadastro, edição, status).
- **Auditorias** — registro de auditorias por rodada.
- **Pagamentos** — controle financeiro por rodada.
- **Por Município** — cobertura geográfica e risco.

Os dados são salvos no Supabase e persistem entre sessões e dispositivos.
""")

st.divider()

with st.expander("ℹ️ Glossário rápido"):
    st.markdown("""
    **Aprovação** (status do cadastro): APROVADO, RESERVA, ELIMINADO, PENDENTE.

    **Status no grupo** (WhatsApp): ADICIONADO AO GRUPO, MENSAGEM ENVIADA, A ADICIONAR, A REMOVER.

    **Decisão atual** (pós-auditoria):
    - APROVADO / APROVADO C/ OBS — pagamento liberado.
    - AJUSTES SIMPLES — retreinamento focal.
    - AJUSTES IMPORTANTES — retreinamento intensivo + reauditoria 100% próxima.
    - ADVERTÊNCIA FINAL — última chance, repetir = eliminação automática.
    - ELIMINADO — fora da operação.
    - AUDITORIA PENDENTE — aguardando análise.
    """)
