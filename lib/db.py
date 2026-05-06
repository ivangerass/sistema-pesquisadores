"""Conexão com Supabase + helpers de banco."""
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    """Retorna cliente Supabase (cached)."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ===== PESQUISADORES =====

def listar_pesquisadores(filtros: dict = None):
    """Lista pesquisadores. filtros = {'municipio': 'X', 'aprovacao': 'Y'}"""
    sb = get_client()
    q = sb.table("pesquisadores").select("*").order("municipio").order("nome")
    if filtros:
        for k, v in filtros.items():
            if v and v != "Todos":
                q = q.eq(k, v)
    return q.execute().data


def get_pesquisador(pid: int):
    sb = get_client()
    res = sb.table("pesquisadores").select("*").eq("id", pid).execute()
    return res.data[0] if res.data else None


def criar_pesquisador(dados: dict):
    sb = get_client()
    return sb.table("pesquisadores").insert(dados).execute()


def atualizar_pesquisador(pid: int, dados: dict):
    sb = get_client()
    return sb.table("pesquisadores").update(dados).eq("id", pid).execute()


def deletar_pesquisador(pid: int):
    sb = get_client()
    return sb.table("pesquisadores").delete().eq("id", pid).execute()


# ===== AUDITORIAS =====

def listar_auditorias(rodada: str = None, pesq_id: int = None):
    sb = get_client()
    q = sb.table("auditorias").select("*, pesquisadores(nome, municipio)").order("data_auditoria", desc=True)
    if rodada and rodada != "Todas":
        q = q.eq("rodada", rodada)
    if pesq_id:
        q = q.eq("pesquisador_id", pesq_id)
    return q.execute().data


def criar_auditoria(dados: dict):
    sb = get_client()
    return sb.table("auditorias").insert(dados).execute()


def atualizar_auditoria(aid: int, dados: dict):
    sb = get_client()
    return sb.table("auditorias").update(dados).eq("id", aid).execute()


def deletar_auditoria(aid: int):
    sb = get_client()
    return sb.table("auditorias").delete().eq("id", aid).execute()


# ===== PAGAMENTOS =====

def listar_pagamentos(rodada: str = None):
    sb = get_client()
    q = sb.table("pagamentos").select("*, pesquisadores(nome, municipio, pix)").order("rodada")
    if rodada and rodada != "Todas":
        q = q.eq("rodada", rodada)
    return q.execute().data


def criar_pagamento(dados: dict):
    sb = get_client()
    return sb.table("pagamentos").insert(dados).execute()


def atualizar_pagamento(pid: int, dados: dict):
    sb = get_client()
    return sb.table("pagamentos").update(dados).eq("id", pid).execute()


# ===== MUNICÍPIOS =====

def listar_municipios():
    sb = get_client()
    return sb.table("municipios").select("*").order("nome").execute().data


def get_meta_municipio(nome: str) -> int:
    sb = get_client()
    res = sb.table("municipios").select("meta").eq("nome", nome).execute()
    return res.data[0]["meta"] if res.data else 1


# ===== AGREGAÇÕES =====

def stats_geral():
    """KPIs principais."""
    sb = get_client()
    pesqs = sb.table("pesquisadores").select("aprovacao, decisao_atual, audit_pendente").execute().data
    return {
        "total": len(pesqs),
        "aprovados": sum(1 for p in pesqs if p["aprovacao"] == "APROVADO"),
        "reservas": sum(1 for p in pesqs if p["aprovacao"] == "RESERVA"),
        "eliminados": sum(1 for p in pesqs if p["aprovacao"] == "ELIMINADO" or p["decisao_atual"] == "ELIMINADO"),
        "advert_final": sum(1 for p in pesqs if p["decisao_atual"] == "ADVERTÊNCIA FINAL"),
        "audit_pendente": sum(1 for p in pesqs if p["audit_pendente"]),
    }


def stats_municipios():
    """Cobertura por município."""
    sb = get_client()
    munis = sb.table("municipios").select("*").execute().data
    pesqs = sb.table("pesquisadores").select("municipio, aprovacao, decisao_atual, status_grupo").execute().data
    
    resultado = []
    for m in munis:
        nome = m["nome"]
        meta = m["meta"]
        ps = [p for p in pesqs if p["municipio"] == nome]
        no_grupo = sum(1 for p in ps if p["status_grupo"] == "ADICIONADO AO GRUPO")
        titulares = sum(1 for p in ps if p["decisao_atual"] in [
            "APROVADO", "APROVADO C/ OBS", "AJUSTES SIMPLES", "AJUSTES IMPORTANTES"
        ])
        reservas = sum(1 for p in ps if p["aprovacao"] == "RESERVA")
        advert = sum(1 for p in ps if p["decisao_atual"] == "ADVERTÊNCIA FINAL")
        ativos = titulares + advert
        
        if ativos == 0:
            risco = "SEM COBERTURA"
        elif ativos < meta:
            risco = "BAIXO"
        else:
            risco = "OK"
        
        resultado.append({
            "Município": nome, "Meta": meta, "No Grupo": no_grupo,
            "Titulares": titulares, "Reservas": reservas,
            "Advert. Final": advert, "Risco": risco,
        })
    return resultado
