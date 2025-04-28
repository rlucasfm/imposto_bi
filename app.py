import base64
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

from modules.analises import show_analises
from modules.dashboard import show_dashboard
from modules.ranking import show_ranking


# Configurações de layout
st.set_page_config(
    page_title="CONAJE - Feirão do Imposto 2024",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "estado_click" not in st.session_state:
    st.session_state["estado_click"] = None

if "estado_foi_clicado" not in st.session_state:
    st.session_state["estado_foi_clicado"] = False


# Estilo personalizado para maximizar a largura
st.markdown("""
    <style>
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


### ------------- CONFIGURAÇÃO BACKGROUND ------------- ###
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    section {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    header {
        background: none !important;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg('bg.jpg')
### ------------- FIM CONFIGURAÇÃO BACKGROUND ------------- ###

# Função para carregar os dados com cache
@st.cache_data(ttl=600)  # Cache por 10 minutos (600 segundos)
def load_data():
    # Conexão com Google Sheets
    url = "https://docs.google.com/spreadsheets/d/16Dds7dImtxM9OwIYBijZtU0gBIfMmQZljXnrMeGLQww/edit?usp=sharing"
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, usecols=list(range(14)), worksheet="1635155053")
    
    # Ajuste nos nomes de colunas
    df.columns = [col.strip().replace(" ", "_").replace("(", "").replace(")", "") for col in df.columns]
    
    # Conversões de tipos
    df["Número_de_Pessoas_impactadas"] = pd.to_numeric(df["Número_de_Pessoas_impactadas"], errors="coerce")
    
    # Tratamento especial para valores monetários (formato brasileiro)
    df["Impacto_Econômico_Estimado_R$"] = df["Impacto_Econômico_Estimado_R$"].apply(
        lambda x: pd.to_numeric(str(x).replace('.', '').replace(',', '.'), errors="coerce")
    )
    
    df["Número_de_Empresas_Apoiadoras"] = pd.to_numeric(df["Número_de_Empresas_Apoiadoras"], errors="coerce")
    df["Alcance_em_Redes_Sociais_Pessoas"] = pd.to_numeric(df["Alcance_em_Redes_Sociais_Pessoas"], errors="coerce")
    df["Quantidade_de_Posts_sobre_a_ação"] = pd.to_numeric(df["Quantidade_de_Posts_sobre_a_ação"], errors="coerce")
    df["Quantidade_de_Likes_nos_Posts"] = pd.to_numeric(df["Quantidade_de_Likes_nos_Posts"], errors="coerce")
    
    return df

# Carrega os dados
df = load_data()
print(df.info())

### ------------- SIDEBAR ------------- ###

# Botões de navegação no sidebar
st.sidebar.markdown("## Navegação")

# Inicializa o estado da página se não existir
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "Dashboard"

# Cria a navegação
pagina = st.sidebar.radio(
    "Navegação",
    ["Dashboard", "Ranking", "Análises"],
    label_visibility="collapsed"
)

# Atualiza o estado e recarrega se mudou
if pagina != st.session_state["pagina"]:
    st.session_state["pagina"] = pagina
    st.rerun()

st.sidebar.markdown("---")

# Adiciona indicador de última atualização
ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
st.sidebar.markdown(f"🔄 Última atualização: {ultima_atualizacao}")

# Botão para forçar atualização
if st.sidebar.button("Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()


### ------------ CABEÇALHO ------------- ###
col1, col2, col3 = st.columns((1, 2, 4))
with col1:
    st.image('logotipo-02.png', width=200)
with col2:
    st.image('logos.png', width=300)
with col3:
    st.markdown("## CONAJE - Feirão do Imposto 2024")    

### ------------- PAGINA ------------- ###
if st.session_state["pagina"] == "Dashboard":
    show_dashboard(df)

if st.session_state["pagina"] == "Ranking":
    show_ranking(df)

if st.session_state["pagina"] == "Análises":
    show_analises(df)
