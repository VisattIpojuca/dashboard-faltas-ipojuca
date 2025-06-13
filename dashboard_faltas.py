import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta, datetime

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
}, inplace=True)

# Converte coluna Data da Falta para datetime
df["Data da Falta"] = pd.to_datetime(df["Data da Falta"], errors='coerce')

# Sidebar - filtros corrigidos
setores = st.sidebar.multiselect(
    "Unidade de Saúde",
    options=sorted(df["Setor"].dropna().unique())
)

funcionarios = st.sidebar.multiselect(
    "Nome do Profissional",
    options=sorted(df["Nome do Funcionário"].dropna().unique())
)

# Configura filtro de datas com padrão últimos 30 dias e intervalo permitido entre 1 e 365 dias
data_min = df["Data da Falta"].min()
data_max = df["Data da Falta"].max()

# Calcula default de data_inicio (máximo entre data_min e 30 dias atrás)
default_start = max(data_min, data_max - timedelta(days=30))

# Inputs de data com limite de intervalo
data_inicio = st.sidebar.date_input(
    "Data inicial",
    value=default_start,
    min_value=data_min,
    max_value=data_max
)

data_fim = st.sidebar.date_input(
    "Data final",
    value=data_max,
    min_value=data_min,
    max_value=data_max
)

# Ajusta para garantir intervalo máximo de 365 dias
if (data_fim - data_inicio).days > 365:
    st.sidebar.warning("O intervalo máximo permitido é de 365 dias. Ajustando data inicial.")
    data_inicio = data_fim - timedelta(days=365)

# Filtra os dados de acordo com os filtros
df_filtrado = df.copy()

if setores:
    df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setores)]

if funcionarios:
    df_filtrado = df_filtrado[df_filtrado["Nome do Funcionário"].isin(funcionarios)]

df_filtrado = df_filtrado[
    (df_filtrado["Data da Falta"] >= pd.to_datetime(data_inicio)) &
    (df_filtrado["Data da Falta"] <= pd.to_datetime(data_fim))
]

st.markdown(f"### 📋 Resumo da Seleção Ativa ({len(df_filtrado)} registros)")

st.dataframe(df_filtrado.reset_index(drop=True))

# Aqui você pode adicionar gráficos ou outras análises

# Exportar CSV dos dados filtrados
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Exportar dados filtrados (.csv)",
    data=csv,
    file_name='faltas_filtradas.csv',
    mime='text/csv',
)

