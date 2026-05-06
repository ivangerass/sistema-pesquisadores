# Sistema de Pesquisadores — Perspectiva 2026

Sistema web (Streamlit + Supabase) para gestão da operação de pesquisa eleitoral no interior do Amazonas.

## Funcionalidades (MVP)

- **Dashboard** — KPIs gerais, cobertura por município, status de pagamentos, próximas ações.
- **Pesquisadores** — base mestra com CRUD e filtros (por município, aprovação, decisão).
- **Auditorias** — registro por rodada (R1, R2, ...) com auditor, resultado e detalhes. Atualiza decisão atual do pesquisador automaticamente.
- **Pagamentos** — controle financeiro por rodada, com status (Liberado / Pago / Bloqueado / Suspenso) e cálculo automático do total.
- **Por Município** — visão geográfica com sinalização de risco e drill-down por município.

---

## Setup do zero — passo a passo (~30 min)

### 1. Criar projeto no Supabase

1. Acesse https://supabase.com → "Start your project" → criar conta gratuita.
2. Clique em **New Project** → escolha um nome (ex.: `pesquisadores-2026`), defina senha do banco (anote), região São Paulo.
3. Aguarde ~2 min até o projeto ficar pronto.

### 2. Criar as tabelas

1. No painel do Supabase, vá em **SQL Editor** → **New query**.
2. Abra o arquivo `seed/01_schema.sql` deste repositório, copie o conteúdo todo e cole no editor SQL.
3. Clique em **Run**. Deve aparecer "Success".

### 3. Importar dados iniciais

1. Ainda no **SQL Editor**, abra `seed/02_seed.sql`, copie e cole tudo.
2. Clique em **Run**. Vai inserir 61 municípios, 76 pesquisadores, 15 auditorias R1 e os pagamentos R1.

### 4. Pegar credenciais do Supabase

1. No painel do projeto, vá em **Settings** (ícone de engrenagem) → **API**.
2. Copie:
   - **Project URL** (formato `https://xxxxx.supabase.co`)
   - **service_role key** (clique em "Reveal" — é uma string longa começando com `eyJ...`)

> ⚠️ A `service_role` ignora RLS — ok pra uso individual privado. Não a exponha publicamente.

### 5. Subir o repositório no GitHub

```bash
cd sistema-pesquisadores
git init
git add .
git commit -m "Sistema de pesquisadores — MVP"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/sistema-pesquisadores.git
git push -u origin main
```

> O `.streamlit/secrets.toml` está no `.gitignore` — credenciais não vão pro GitHub.

### 6. Deploy no Streamlit Community Cloud

1. Acesse https://share.streamlit.io → **Sign in with GitHub**.
2. Clique em **New app** → escolha o repositório, branch `main`, arquivo `app.py`.
3. Antes de clicar em Deploy, vá em **Advanced settings** → **Secrets** e cole:

```toml
SUPABASE_URL = "https://SEUPROJETO.supabase.co"
SUPABASE_KEY = "eyJ... (cole a service_role key aqui)"
APP_PASSWORD = "escolha-uma-senha-forte"
```

4. **Deploy!** Em ~2 min seu app estará no ar em `https://NOMEDOAPP.streamlit.app`.

---

## Rodar localmente (opcional)

Se quiser testar antes de subir:

```bash
# Pré-requisitos: Python 3.10+
cd sistema-pesquisadores

# Crie um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

# Instale dependências
pip install -r requirements.txt

# Configure os secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edite .streamlit/secrets.toml com suas credenciais

# Rode
streamlit run app.py
```

App abre automaticamente em http://localhost:8501.

---

## Estrutura do projeto

```
sistema-pesquisadores/
├── app.py                     # Entry point (login + landing)
├── pages/                     # Streamlit detecta automaticamente
│   ├── 1_📊_Dashboard.py
│   ├── 2_👥_Pesquisadores.py
│   ├── 3_🔍_Auditorias.py
│   ├── 4_💰_Pagamentos.py
│   └── 5_🗺️_Por_Município.py
├── lib/
│   ├── db.py                  # Conexão Supabase + helpers CRUD
│   ├── auth.py                # Login por senha
│   └── const.py               # Listas de dropdowns
├── seed/
│   ├── 01_schema.sql          # CREATE TABLE
│   └── 02_seed.sql            # INSERTs com dados iniciais
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── .gitignore
```

---

## Próximas iterações sugeridas

- **Comunicação** — log de mensagens WhatsApp enviadas, com templates por categoria.
- **Reposições** — histórico de quem entrou/saiu da operação.
- **Exportar relatórios** — PDF e Excel com filtros aplicados.
- **Gráficos** — evolução de pesquisas por rodada, distribuição de decisões.
- **Notificações** — e-mail quando auditoria pendente passa de X dias.

---

## Suporte

Em caso de erro: confira que (1) os secrets estão corretos, (2) o schema rodou sem erro no Supabase, (3) os dados foram inseridos via `02_seed.sql`.
