# 🛰️ FAD – Ferramenta de Análise Dinamizada

---

## 1. O que é e o que a FAD faz

A **FAD** é uma plataforma web open-source voltada para a análise espacial e ambiental de geometrias (shapefiles de linhas), desenvolvida para apoiar tecnicamente os processos de estadualização e licenciamento ambiental de rodovias no Estado de São Paulo.

Ela permite importar, validar e cruzar geometrias com dados oficiais, classificando automaticamente sobreposições com áreas protegidas e gerando laudos e relatórios técnicos completos.

---

## 2. Características da Arquitetura Computacional

- ✅ 100% baseada em **ferramentas open-source**
- ✅ Interface web construída com **FastAPI** e **Jinja2**
- ✅ Armazenamento em banco **PostgreSQL com extensão PostGIS**
- ✅ Geração de relatórios em PDF com **ReportLab**
- ✅ Gerenciamento de usuários com **controle de sessão**
- ✅ Pronta para rodar via **GitHub Codespaces**, sem instalação local

---

## 3. Módulos

### Módulos definidos na FAD:

1. **Controle de Usuários** ✅  
2. **Cadastro de Interessados** ⚙️  
3. **Importação e Validação de Geometrias** ✅  
4. **Conformidade Ambiental** ✅  
5. **Favorabilidade Multicritério** ❌ (*não implementado*)  
6. **Favorabilidade Socioeconômica** ❌ (*não implementado*)  
7. **Favorabilidade Infraestrutural** ❌ (*não implementado*)

---

### 3.1 Módulo Controle de Usuários

**O que é:**  
Permite o cadastro, autenticação e controle de acesso de operadores da FAD.

**O que faz:**
- Cria usuários com perfil `comum` ou `master`
- Gera hash seguro das senhas
- Controla sessão ativa

**Arquivos e funções:**
- `cd_autenticacao.py`, `cd_cadastro.py`, `cd_login.html`, `cd_painel_usuario.html`, `cd_painel_master.html`

---

### 3.2 Módulo Cadastro de Interessados

**O que é:**  
Gerencia o cadastro de clientes que demandarão os serviços da FAD (pessoas físicas e jurídicas).

**O que faz:**
- Permite cadastrar interessados com CPF ou CNPJ
- Cadastra representante legal vinculado à PJ
- Armazena dados de contato e identificação no banco

**Arquivos e funções:**
- `cd_interessado.py`, `cd_cadastro.html`, `cd_cadastro_form.html`

---

### 3.3 Módulo Importação e Validação de Geometrias

**O que é:**  
Recebe e valida shapefiles (zip) enviados pelo usuário.

**O que faz:**
- Verifica arquivos .shp, .shx, .prj, .dbf
- Verifica coluna `Cod`, geometria nula e SRID
- Gera relatório PDF

**Arquivos e funções:**
- `upload.py`, `validacao_geometria.py`, `relatorio_upload.py`, `relatorio_validacao.py`

---

### 3.4 Módulo Conformidade Ambiental

**O que é:**  
Analisa a conformidade da geometria com camadas de áreas protegidas.

**O que faz:**
- Realiza interseção com dados do DataGEO
- Classifica como Risco / Restrição / Livre
- Gera laudo analítico ou sintético + shapefile de interseções

**Arquivos e funções:**
- `ca_processador.py`, `ca_processamento.py`, `ca_laudo.py`, `ca_laudo_sintetico.py`, `ca_mapa.py`, `ca_endpoint.py`

---

### 3.5 Módulos Não Implementados

- **Favorabilidade Multicritério**
- **Favorabilidade Socioeconômica**
- **Favorabilidade Infraestrutural**

---

## 4. Módulos Implementados

✅ Controle de Usuários  
✅ Importação e Validação de Geometrias  
✅ Conformidade Ambiental  
⚙️ Cadastro de Interessados (estrutura pronta)

---

## 5. Próximos Passos

- Finalizar UI do Cadastro de Interessados  
- Iniciar Favorabilidade Multicritério  
- Estruturar exportação shapefile final  
- Criar painel de projetos processados

---

## 📎 Anexo A – Estrutura Atual do Projeto

*(Use o comando `tree` ou `find app/` para gerar automaticamente)*

---

## 📎 Anexo B – Arquivos Técnicos Complementares

- `core/jinja.py`: configuração Jinja  
- `database/base.py`, `session.py`: base e sessão SQLAlchemy  
- `models/trechos_validados.py`, `arquivos.py`: estruturas auxiliares  
- `templates/home.html`, `index.html`: páginas principais da interface

