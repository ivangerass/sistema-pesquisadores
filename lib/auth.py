"""Autenticação simples por senha (uso individual)."""
import streamlit as st


def check_password() -> bool:
    """Bloqueia acesso até a senha correta ser fornecida."""
    if st.session_state.get("password_correct", False):
        return True

    st.markdown("### 🔒 Sistema de Pesquisadores — Perspectiva 2026")
    st.caption("Acesso restrito.")
    pwd = st.text_input("Senha", type="password", key="pwd_input")
    if st.button("Entrar", type="primary"):
        if pwd == st.secrets.get("APP_PASSWORD"):
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False


def logout_button():
    """Botão de logout no sidebar."""
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.password_correct = False
        st.rerun()
