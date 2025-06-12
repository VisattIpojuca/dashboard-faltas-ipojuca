
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

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
setores = st.sidebar.multiselect("Unidade de Saúde", sorted(df["Setor"].unique()))
funcionarios = st.sidebar.multiselect("Nome do Profissional", sorted(df["Nome do Funcionário"].unique()))
cargos = st.sidebar.multiselect("Motivo da Falta", sorted(df["Motivo"].unique()))
ano = st.sidebar.selectbox("Ano", sorted(df["Ano"].dropna().unique()), index=0)

# Aplica os filtros
df_filtrado = df.copy()
if setores:
    df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setores)]
if funcionarios:
    df_filtrado = df_filtrado[df_filtrado["Nome do Funcionário"].isin(funcionarios)]
if cargos:
    df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(cargos)]
if ano:
    df_filtrado = df_filtrado[df_filtrado["Ano"] == ano]

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
st.subheader("📋 Tabela Detalhada")
st.dataframe(df_filtrado, use_container_width=True)

# Download CSV
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar como CSV", data=csv, file_name="faltas_filtradas.csv", mime="text/csv")

# Download XLSX
xlsx_buffer = BytesIO()
with pd.ExcelWriter(xlsx_buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Faltas')
    writer.save()
st.download_button("📥 Baixar como XLSX", data=xlsx_buffer.getvalue(), file_name="faltas_filtradas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
