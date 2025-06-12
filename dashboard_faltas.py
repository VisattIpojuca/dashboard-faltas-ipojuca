
import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações da página
st.set_page_config(page_title="Dashboard de Faltas - Vigilância em Saúde", layout="wide")
st.title("📊 Dashboard de Faltas dos Funcionários - Vigilância em Saúde de Ipojuca")

# ID e nome da aba
sheet_id = "1vf27HR8Pk-CiS_zT-1-0oskfsMlR6DPM63OX61SJzU0"
sheet_name = "Respostas ao formulário 1"

# Converte para CSV (Google Sheets)
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Lê os dados
df = pd.read_csv(url)
df.columns = [col.strip() for col in df.columns]

# Renomeia colunas
df.rename(columns={
    df.columns[0]: "Data de Envio",
    df.columns[1]: "Nome do Funcionário",
    df.columns[2]: "Setor",
    df.columns[3]: "Data da Falta",
    df.columns[4]: "Motivo",
    df.columns[5]: "Observações"
}, inplace=True)

# Conversões
df["Data da Falta"] = pd.to_datetime(df["Data da Falta"], errors='coerce')
df["Ano"] = df["Data da Falta"].dt.year
df["Mês"] = df["Data da Falta"].dt.month_name()

# Filtros
st.sidebar.header("🔍 Filtros")
funcionarios = st.sidebar.multiselect("Funcionário", df["Nome do Funcionário"].unique())
setores = st.sidebar.multiselect("Setor", df["Setor"].unique())
motivos = st.sidebar.multiselect("Motivo da Falta", df["Motivo"].unique())
ano = st.sidebar.selectbox("Ano", sorted(df["Ano"].dropna().unique()), index=0)

# Aplica filtros
df_filtrado = df.copy()
if funcionarios:
    df_filtrado = df_filtrado[df_filtrado["Nome do Funcionário"].isin(funcionarios)]
if setores:
    df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setores)]
if motivos:
    df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(motivos)]
if ano:
    df_filtrado = df_filtrado[df_filtrado["Ano"] == ano]

# Métricas
st.subheader("📈 Visão Geral")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Faltas", len(df_filtrado))
col2.metric("Funcionários", df_filtrado["Nome do Funcionário"].nunique())
col3.metric("Setores", df_filtrado["Setor"].nunique())

# Gráficos
st.subheader("📊 Distribuição de Faltas")
col4, col5 = st.columns(2)
with col4:
    fig1 = px.histogram(df_filtrado, x="Motivo", color="Setor", title="Faltas por Motivo")
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    fig2 = px.histogram(df_filtrado, x="Mês", color="Setor", title="Faltas por Mês")
    st.plotly_chart(fig2, use_container_width=True)

# Tabela
st.subheader("📋 Tabela Detalhada")
st.dataframe(df_filtrado, use_container_width=True)

# Download
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar dados filtrados", data=csv, file_name="faltas_filtradas.csv", mime="text/csv")
