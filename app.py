import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
from datetime import datetime


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


# Adiciona indicador de última atualização
ultima_atualizacao = datetime.now().strftime("%H:%M:%S")
st.sidebar.markdown(f"🔄 Última atualização: {ultima_atualizacao}")

# Botão para forçar atualização
if st.sidebar.button("Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# KPIs
kpis = {
    "Pessoas Impactadas": int(df["Número_de_Pessoas_impactadas"].sum()),
    "Impacto Econômico (R$)": float(df['Impacto_Econômico_Estimado_R$'].sum()),
    "Empresas Apoiadoras": int(df["Número_de_Empresas_Apoiadoras"].sum()),
    "Ações Realizadas": df.shape[0],
    "Alcance Redes Sociais": int(df["Alcance_em_Redes_Sociais_Pessoas"].sum()),
    "Quantidade de Posts": int(df["Quantidade_de_Posts_sobre_a_ação"].sum()),
    "Quantidade de Curtidas": int(df["Quantidade_de_Likes_nos_Posts"].sum())
}

# Cabeçalho
st.markdown("## CONAJE - Feirão do Imposto 2024")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric("Pessoas Impactadas", f"{kpis['Pessoas Impactadas']:,}".replace(",", "."))
col2.metric("Impacto Econômico (R$)", f"R$ {kpis['Impacto Econômico (R$)']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Empresas Apoiadoras", f"{kpis['Empresas Apoiadoras']:,}".replace(",", "."))
col4.metric("Ações Realizadas", kpis["Ações Realizadas"])
col5.metric("Alcance Redes Sociais", f"{kpis['Alcance Redes Sociais']:,}".replace(",", "."))
col6.metric("Qtd. de Posts", f"{kpis['Quantidade de Posts']:,}".replace(",", "."))
col7.metric("Qtd. de Curtidas", f"{kpis['Quantidade de Curtidas']:,}".replace(",", "."))

# Filtros principais
movimentos = df["Tipo_de_Ação"].dropna().unique().tolist()
estados = df["Estado"].dropna().unique().tolist()
coberturas = df["Tipo_de_Cobertura"].dropna().unique().tolist()
tipos_acao = df["Tipo_de_Ação"].dropna().unique().tolist()

# Inicializa o estado clicado
if "estado_click" not in st.session_state:
    st.session_state["estado_click"] = None

# Filtros
if st.button("🔄 Resetar todos os filtros"):
    st.session_state["filtro_mov"] = []
    st.session_state["filtro_estado"] = []
    st.session_state["filtro_cobertura"] = []
    st.session_state["filtro_acao"] = []
    st.session_state["estado_click"] = None
    st.rerun()
    
f1, f2, f3, f4 = st.columns(4)

filtro_mov = f1.multiselect("Movimento:", sorted(movimentos), key="filtro_mov", placeholder="Selecione um movimento")
estado_default = st.session_state["estado_click"]

# Só usar como default se o estado clicado existir entre as opções disponíveis
if estado_default not in estados:
    estado_default = None
# Se já processou o clique, zera o gatilho
if st.session_state.get("estado_foi_clicado"):
    st.session_state["estado_foi_clicado"] = False
filtro_estado = f2.multiselect(
    "Estado:",
    sorted(estados),
    default=[estado_default] if estado_default else [],
    key="filtro_estado",
    placeholder="Selecione um estado"
)
filtro_cobertura = f3.multiselect("Tipo Cobertura:", sorted(coberturas), key="filtro_cobertura", placeholder="Selecione uma cobertura")
filtro_acao = f4.multiselect("Ação:", sorted(tipos_acao), key="filtro_acao", placeholder="Selecione uma ação")


df_filtrado = df.copy()

if filtro_mov:
    df_filtrado = df_filtrado[df_filtrado["Tipo_de_Ação"].isin(filtro_mov)]
if filtro_estado:
    df_filtrado = df_filtrado[df_filtrado["Estado"].isin(filtro_estado)]
if filtro_cobertura:
    df_filtrado = df_filtrado[df_filtrado["Tipo_de_Cobertura"].isin(filtro_cobertura)]
if filtro_acao:
    df_filtrado = df_filtrado[df_filtrado["Tipo_de_Ação"].isin(filtro_acao)]

# Criando o layout com duas colunas principais
col_mapa, col_graficos = st.columns([0.4, 0.6])

with col_mapa:
    # Lista de todos os estados brasileiros por sigla
    estados_brasil = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
                    'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
    # DataFrame auxiliar
    df_todos_estados = pd.DataFrame({"Estado": estados_brasil})
    # Agrupar os dados reais
    df_mapa = df_filtrado.groupby("Estado")["Número_de_Pessoas_impactadas"].sum().reset_index()
    # Mesclar com os estados que não aparecem
    df_mapa = df_todos_estados.merge(df_mapa, on="Estado", how="left").fillna(0)

    st.markdown("### Localização VS Movimento")
    
    # Importar GeoJSON com estados do Brasil (siglas)
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson_data = requests.get(geojson_url).json()
    
    # Cria mapa base
    m = folium.Map(location=[-14.2, -51.9], zoom_start=4, tiles="cartodb positron")
    
    # Cria dicionário para acesso rápido aos valores por estado
    valores = dict(zip(df_mapa["Estado"], df_mapa["Número_de_Pessoas_impactadas"]))
    
    # Estilo das regiões no mapa
    def style_function(feature):
        sigla = feature["properties"]["sigla"]
        valor = valores.get(sigla, 0)
        cor = "#000000" if valor == 0 else "#444444"
        return {
            'fillColor': cor,
            'color': 'white',
            'weight': 1,
            'fillOpacity': 0.6,
        }

    # Cria choropleth com base em intensidade
    choropleth = folium.Choropleth(
        geo_data=geojson_data,
        name="Choropleth",
        data=df_mapa,
        columns=["Estado", "Número_de_Pessoas_impactadas"],
        key_on="feature.properties.sigla",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Pessoas Impactadas",
        highlight=True
    ).add_to(m)

    # Adiciona tooltip com nome e valor
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=["sigla", "name"],
            aliases=["UF:", "Estado:"],
            labels=True,
            sticky=False
        )
    )


    # Renderiza no Streamlit
    resultado = st_folium(m, width=700, height=500)
    
    # Verifica clique
    if resultado:  # se resultado não é None
        last_active = resultado.get("last_active_drawing")
        if last_active:  # se last_active não é None
            properties = last_active.get("properties")
            if properties:  # se properties não é None
                sigla_clicada = properties.get("sigla")
                if sigla_clicada and sigla_clicada != st.session_state["estado_click"]:
                    st.session_state["estado_click"] = sigla_clicada
                    st.session_state["estado_foi_clicado"] = True
                    st.rerun()


with col_graficos:
    # ========== GRÁFICO 2: Pessoas vs Estado ==========
    st.markdown("### Pessoas VS Estado:")
    
    df_estado = df_filtrado.groupby("Estado").agg({
        "Número_de_Pessoas_impactadas": "sum",
        "Data_da_Ação": "count"
    }).rename(columns={"Data_da_Ação": "Qtd_Ações"}).reset_index()
    
    fig_estado = go.Figure()
    
    fig_estado.add_trace(go.Bar(
        x=df_estado["Estado"],
        y=df_estado["Número_de_Pessoas_impactadas"],
        name="Qtd Pessoas",
        marker_color="green"
    ))
    
    fig_estado.add_trace(go.Scatter(
        x=df_estado["Estado"],
        y=df_estado["Qtd_Ações"],
        name="Qtd Ações",
        yaxis="y2",
        mode="lines+markers",
        marker=dict(color="white"),
        line=dict(dash='dot')
    ))
    
    fig_estado.update_layout(
        yaxis=dict(title="Pessoas"),
        yaxis2=dict(title="Ações", overlaying='y', side='right'),
        barmode='group',
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=40, r=40, t=40, b=40),
        height=300
    )
    
    st.plotly_chart(fig_estado, use_container_width=True)

    # ========== GRÁFICO 3: Pessoas vs Tipo de Ação ==========
    st.markdown("### Pessoas VS Ação")

    df_acao = df_filtrado.groupby("Tipo_de_Ação")["Número_de_Pessoas_impactadas"].sum().reset_index()

    fig_acao = px.bar(
        df_acao.sort_values(by="Número_de_Pessoas_impactadas", ascending=False),
        x="Tipo_de_Ação",
        y="Número_de_Pessoas_impactadas",
        text_auto=True,
        title="",
        labels={"Número_de_Pessoas_impactadas": "Pessoas", "Tipo_de_Ação": "Ação"}
    )
    fig_acao.update_layout(xaxis_tickangle=-20, margin=dict(t=20, b=80))
    st.plotly_chart(fig_acao, use_container_width=True)


# ============= DETALHAMENTO POR MOVIMENTO =============
st.markdown("### 📊 Detalhamento por Tipo de Ação e Movimento")

# Formatador monetário em JS
money_formatter = JsCode("""
function(params) {
    return 'R$ ' + params.value.toLocaleString('pt-BR');
}
""")


# Agrupa por Tipo de Ação + Movimento
df_aggrid = df_filtrado.groupby(["Tipo_de_Ação", "Movimento"]).agg({
    "Número_de_Pessoas_impactadas": "sum",
    "Data_da_Ação": "count",
    "Número_de_Empresas_Apoiadoras": "sum",
    "Impacto_Econômico_Estimado_R$": "sum"
}).reset_index().rename(columns={
    "Número_de_Pessoas_impactadas": "Pessoas",
    "Data_da_Ação": "Ações",
    "Número_de_Empresas_Apoiadoras": "Empresas",
    "Impacto_Econômico_Estimado_R$": "Impacto Econômico"
})
# Linha de total
linha_total = pd.DataFrame([{
    "Tipo_de_Ação": "🔹 Total",
    "Movimento": "🔹 Total",
    "Pessoas": df_aggrid["Pessoas"].sum(),
    "Ações": df_aggrid["Ações"].sum(),
    "Empresas": df_aggrid["Empresas"].sum(),
    "Impacto Econômico": df_aggrid["Impacto Econômico"].sum()
}])

# Junta
df_aggrid_total = pd.concat([df_aggrid, linha_total], ignore_index=True)

# Formatar como inteiro
for col in ["Pessoas", "Ações", "Empresas"]:
    df_aggrid_total[col] = df_aggrid_total[col].fillna(0).astype(int)


# Build Grid
gb = GridOptionsBuilder.from_dataframe(df_aggrid_total)
gb.configure_grid_options(groupDisplayType="groupRows")
gb.configure_column("Tipo_de_Ação", rowGroup=True, hide=True)
gb.configure_column("Impacto Econômico", type=["numericColumn"], valueFormatter=money_formatter)



grid_options = gb.build()

# Renderizar
AgGrid(
    df_aggrid_total,
    gridOptions=grid_options,
    enable_enterprise_modules=True,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    theme="balham-dark",  # Usa dark como base
    height=420
)