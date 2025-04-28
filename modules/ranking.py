import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_ranking(df):
    dados = df.copy()
    
    st.title("Ranking")
    st.write("Aqui você pode ver uma prévia do ranking dos movimentos para cada categoria.")
    st.markdown("---")

    # Criar 2 colunas
    col1, col2 = st.columns(2)

    # ------ Ranking por Pontos de Cobertura de Imprensa ------
    with col1:
        st.markdown("## Maior Cobertura de Imprensa")
        # 1. Criar um dicionário com os tipos e pontuação
        pontuacoes = {
            'Nota em Jornal/Portal de Notícias': 15,
            'Entrevista no Rádio': 20,
            'Matéria ao Vivo - Regional': 25,
            'Matéria ao Vivo - Estadual': 30,
            'Matéria ao Vivo - Nacional': 45,
            'Matéria Gravada - Regional': 20,
            'Matéria Gravada - Estadual': 25,
            'Matéria Gravada - Nacional': 40
        }

        # 2. Criar nova coluna com a pontuação atribuída
        dados["Pontos_Cobertura"] = dados["Tipo_de_Cobertura"].map(pontuacoes).fillna(0)

        # 3. Agrupar por Movimento e somar as pontuações
        ranking_cobertura = dados.groupby("Movimento")["Pontos_Cobertura"].sum().reset_index()

        # 4. Ordenar do maior para o menor
        ranking_cobertura = ranking_cobertura.sort_values(by="Pontos_Cobertura", ascending=False)
        
        # Criar gráfico de barras horizontais
        fig = px.bar(
            ranking_cobertura,
            x="Pontos_Cobertura",
            y="Movimento",
            orientation='h',
            title="Ranking por Pontos de Cobertura de Imprensa",
            labels={
                "Pontos_Cobertura": "Pontuação Total",
                "Movimento": "Movimento"
            }
        )

        # Personalizar layout
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            height=max(400, len(ranking_cobertura)*30),
            margin=dict(l=10, r=10, t=40, b=10)
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

    # ------ Ranking por Pontos de Engajamento das Redes Sociais ------
    with col2:
        st.markdown("## Maior Engajamento nas Redes Sociais")

        # 1. Criar um dicionário com os tipos e pontuação
        # 1. Pontuação por post
        dados['Pontos_Posts'] = dados['Quantidade_de_Posts_sobre_a_ação'] * 10

        # 2. Pontuação triplo-duplo (likes >= 50)
        dados['Pontos_TriploDuplo'] = dados['Quantidade_de_Likes_nos_Posts'].apply(lambda x: 10 if x >= 50 else 0)

        # 3. Pontuação total
        dados['Pontos_Engajamento'] = dados['Pontos_Posts'] + dados['Pontos_TriploDuplo']

        # 4. Agrupamento por movimento
        ranking_engajamento  = dados.groupby('Movimento')['Pontos_Engajamento'].sum().reset_index()
        ranking_engajamento = ranking_engajamento.sort_values(by='Pontos_Engajamento', ascending=False)

        # Criar gráfico de barras horizontais
        fig = px.bar(
            ranking_engajamento,
            x="Pontos_Engajamento",
            y="Movimento",
            orientation='h',
            title="Ranking por Pontos de Engajamento nas Redes Sociais",
            labels={
                "Pontos_Engajamento": "Pontuação Total",
                "Movimento": "Movimento"    
            }
        )

        # Personalizar layout
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            height=max(400, len(ranking_engajamento)*30),
            margin=dict(l=10, r=10, t=40, b=10)
        )

        # Exibir o gráfico  
        st.plotly_chart(fig, use_container_width=True)

    # Criar uma nova linha com 2 colunas
    col3, col4 = st.columns(2)

    # ------ Ranking por Pontos de Conscientização Socioeducacional ------
    with col3:
        st.markdown("## Maior Conscientização Socioeducacional")

        # 1. Pontuação por post
        dados["Pontos_Conscientizacao"] = dados["Número_de_Pessoas_impactadas"] * 0.01
        
        # 2. Agrupamento por movimento
        ranking_conscientizacao = dados.groupby('Movimento')['Pontos_Conscientizacao'].sum().reset_index()
        ranking_conscientizacao = ranking_conscientizacao.sort_values(by='Pontos_Conscientizacao', ascending=False)

        # Criar gráfico de barras horizontais
        fig = px.bar(
            ranking_conscientizacao,
            x="Pontos_Conscientizacao",
            y="Movimento",
            orientation='h',
            title="Ranking por Pontos de Conscientização Socioeducacional",
            labels={
                "Pontos_Conscientizacao": "Pontuação Total",
                "Movimento": "Movimento"
            }
        )

        # Personalizar layout   
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            height=max(400, len(ranking_conscientizacao)*30),
            margin=dict(l=10, r=10, t=40, b=10)
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

    # ------ Ranking por Pontos de Impacto Econômico ------
    with col4:
        st.markdown("## Maior Impacto Econômico")

        # 1. Pontuação por impacto econômico
        dados["Pontos_Impacto"] = (30) + (dados["Impacto_Econômico_Estimado_R$"] * 0.012) + (dados["Número_de_Empresas_Apoiadoras"] * 10)
        
        # 2. Agrupamento por movimento
        ranking_impacto = dados.groupby('Movimento')['Pontos_Impacto'].sum().reset_index()
        ranking_impacto = ranking_impacto.sort_values(by='Pontos_Impacto', ascending=False)

        # Criar gráfico de barras horizontais
        fig = px.bar(
            ranking_impacto,
            x="Pontos_Impacto",
            y="Movimento",
            orientation='h',
            title="Ranking por Pontos de Impacto Econômico",
            labels={
                "Pontos_Impacto": "Pontuação Total",
                "Movimento": "Movimento"
            }
        )

        # Personalizar layout
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            height=max(400, len(ranking_impacto)*30),
            margin=dict(l=10, r=10, t=40, b=10)
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

    # Criar uma nova linha com 2 colunas para o ranking total
    col5, col6 = st.columns(2)

    # ------ Ranking Total (Todas as Métricas) ------
    with col5:
        st.markdown("## Ranking Total")

        # Calcular pontuação total combinando todas as métricas
        dados["Pontuação_Total"] = (
            dados["Pontos_Conscientizacao"] + 
            dados["Pontos_Impacto"] +
            dados["Pontos_Engajamento"] +
            dados["Pontos_Cobertura"]
        )
        
        # Agrupar por movimento
        ranking_total = dados.groupby('Movimento')['Pontuação_Total'].sum().reset_index()
        ranking_total = ranking_total.sort_values(by='Pontuação_Total', ascending=False)

        # Criar gráfico de barras horizontais
        fig = px.bar(
            ranking_total,
            x="Pontuação_Total", 
            y="Movimento",
            orientation='h',
            title="Ranking Total (Cobertura + Engajamento + Conscientização + Impacto Econômico)",
            labels={
                "Pontuação_Total": "Pontuação Total",
                "Movimento": "Movimento"
            }
        )

        # Personalizar layout
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'},
            height=max(400, len(ranking_total)*30),
            margin=dict(l=10, r=10, t=40, b=10)
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

    # ------ Gráfico de Radar para Comparação de Métricas ------
    with col6:
        st.markdown("## Comparação de Métricas")

        # Preparar dados para o gráfico de radar
        metricas = ['Pontos_Cobertura', 'Pontos_Engajamento', 'Pontos_Conscientizacao', 'Pontos_Impacto']
        nomes_metricas = ['Cobertura', 'Engajamento', 'Conscientização', 'Impacto']

        # Criar um DataFrame com as médias normalizadas de cada métrica
        df_radar = pd.DataFrame()
        for metrica, nome in zip(metricas, nomes_metricas):
            df_radar[nome] = dados.groupby('Movimento')[metrica].mean()

        # Normalizar os valores para escala de 0 a 1
        df_radar_normalizado = df_radar / df_radar.max()

        # Criar o gráfico de radar
        fig = go.Figure()

        # Adicionar cada movimento como uma linha no radar
        for movimento in df_radar_normalizado.index:
            fig.add_trace(go.Scatterpolar(
                r=df_radar_normalizado.loc[movimento].values,
                theta=nomes_metricas,
                fill='toself',
                name=movimento
            ))

        # Personalizar o layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Comparação de Desempenho por Métrica",
            height=500
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

