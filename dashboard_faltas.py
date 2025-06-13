import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações da página
st.set_page_config(page_title="Dashboard de Faltas - APS Ipojuca", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }
    .css-18e3th9 {
        background-color: #004a99 !important;
    }
    .st-bw {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Faltas dos Funcionários - APS Ipojuca")

# Fonte de dados
sheet_id = "1vf27HR8Pk-CiS_zT-1-0oskfsMlR6DPM63OX61SJzU0"
sheet_name = "respostas1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Lê os dados
df = pd.read_csv(url)
df.columns = [col.strip() for col in df.columns]
df.rename(columns={
    df.columns[0]: "Data de Envio",
    df.columns[1]: "Nome do Funcionário",
    df.columns[2]: "Setor",
    df.columns[3]: "Data da Falta",
    df.columns[4]: "Motivo",
    df.columns[5]: "Observações"
}, inplace=True)

df["Data da Falta"] = pd.to_datetime(df["Data da Falta"], errors='coerce')
df["Ano"] = df["Data da Falta"].dt.year
df["Mês"] = df["Data da Falta"].dt.month_name()

# Filtros
st.sidebar.header("🔍 Filtros")
funcionarios = st.sidebar.multiselect("Unidade de Saúde", sorted(df["Nome do Funcionário"].unique()))
setores = st.sidebar.multiselect("Nome do Profissional", sorted(df["Setor"].unique()))
cargos = st.sidebar.multiselect("Motivo da Falta", sorted(df["Motivo"].unique()))
data_inicio = st.sidebar.date_input("Data inicial")
data_fim = st.sidebar.date_input("Data final")

# Aplica os filtros
df_filtrado = df.copy()
if setores:
    df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setores)]
if funcionarios:
    df_filtrado = df_filtrado[df_filtrado["Nome do Funcionário"].isin(funcionarios)]
if cargos:
    df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(cargos)]
if data_inicio and data_fim:
    df_filtrado = df_filtrado[(df_filtrado["Data da Falta"] >= pd.to_datetime(data_inicio)) & (df_filtrado["Data da Falta"] <= pd.to_datetime(data_fim))]

# Resumo individual (se apenas 1 profissional filtrado)
if len(funcionarios) == 1:
    st.markdown("### 🧾 Resumo do Profissional Selecionado")
    resumo = df_filtrado[["Data da Falta", "Motivo", "Observações"]].sort_values("Data da Falta", ascending=False)
    st.dataframe(resumo, use_container_width=True)

# Métricas
total_faltas = len(df_filtrado)
unique_funcionarios = df_filtrado["Nome do Funcionário"].nunique()
unique_setores = df_filtrado["Setor"].nunique()

st.subheader("📈 Visão Geral")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Faltas", total_faltas)
col2.metric("Funcionários", unique_funcionarios)
col3.metric("Unidades", unique_setores)

# Gráficos
st.subheader("📊 Distribuição de Faltas")
col4, col5 = st.columns(2)
with col4:
    fig1 = px.histogram(df_filtrado, x="Motivo", color="Setor", title="Faltas por Motivo")
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    fig2 = px.histogram(df_filtrado, x="Mês", color="Setor", title="Faltas por Mês")
    st.plotly_chart(fig2, use_container_width=True)

# Tabela detalhada
st.subheader("📋 Resumo da Seleção Ativa")
st.dataframe(df_filtrado, use_container_width=True)

# Download CSV
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar como CSV", data=csv, file_name="faltas_filtradas.csv", mime="text/csv")
