import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo}{valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo}{valor:.2f} milhões'

st.title("DASHBOARD DE VENDAS")

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Selecione a Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todos os anos', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.number_input('Selecione o Ano', min_value = 2020, max_value = 2023, value = 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = "%d/%m/%Y")

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
receita_estados = dados.groupby('Local da compra')['Preço'].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month

receita_categorias = dados.groupby('Categoria do Produto')['Preço'].sum().sort_values(ascending = False).reset_index()

## Tabelas - Quantidade de Vendas

quantidade_estados = (
    dados.groupby('Local da compra')
    .size()
    .reset_index(name='Quantidade')
)

quantidade_estados = (
    dados.drop_duplicates(subset='Local da compra')[
        ['Local da compra', 'lat', 'lon']
    ]
    .merge(
        quantidade_estados,
        on='Local da compra'
    )
    .sort_values('Quantidade', ascending=False)
)


quantidade_mensal = (
    dados
    .set_index('Data da Compra')
    .groupby(pd.Grouper(freq='ME'))
    .size()
    .reset_index(name='Quantidade')
)

quantidade_mensal['Ano'] = quantidade_mensal['Data da Compra'].dt.year
quantidade_mensal['Mês'] = quantidade_mensal['Data da Compra'].dt.month


quantidade_categorias = (
    dados.groupby('Categoria do Produto')
    .size()
    .reset_index(name='Quantidade')
    .sort_values('Quantidade', ascending=False)
)

###Tabela de Vendedores
vendedores = dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])


## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat', 
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False}, 
                                  title = 'Receita por Estado'
)

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Data da Compra',
                             y = 'Preço',
                             markers = True,
                             range_y = [0, receita_mensal['Preço'].max()],
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal'
                             )
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top Estados por Receita'
)

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                x = 'Categoria do Produto',
                                y = 'Preço',
                                text_auto = True,
                                title = 'Receita por Categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Gráficos - Quantidade de Vendas

fig_mapa_quantidade = px.scatter_geo(
    quantidade_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Quantidade',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={
        'lat': False,
        'lon': False,
        'Quantidade': True
    },
    title='Quantidade de Vendas por Estado'
)


fig_quantidade_mensal = px.line(
    quantidade_mensal,
    x='Data da Compra',
    y='Quantidade',
    markers=True,
    range_y=[0, quantidade_mensal['Quantidade'].max()],
    color='Ano',
    line_dash='Ano',
    title='Quantidade de Vendas Mensal'
)

fig_quantidade_mensal.update_layout(
    yaxis_title='Quantidade de Vendas',
    xaxis_title='Data'
)


fig_quantidade_estados = px.bar(
    quantidade_estados.head(),
    x='Local da compra',
    y='Quantidade',
    text_auto=True,
    title='Top Estados por Quantidade de Vendas'
)

fig_quantidade_estados.update_layout(
    yaxis_title='Quantidade de Vendas',
    xaxis_title='Estado'
)


fig_quantidade_categorias = px.bar(
    quantidade_categorias,
    x='Categoria do Produto',
    y='Quantidade',
    text_auto=True,
    title='Quantidade de Vendas por Categoria'
)

fig_quantidade_categorias.update_layout(
    yaxis_title='Quantidade de Vendas',
    xaxis_title='Categoria'
)

## Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$ '))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        st.metric(
            'Quantidade de Vendas',
            formata_numero(dados.shape[0]))

        st.plotly_chart(
            fig_mapa_quantidade,
            use_container_width=True )

        st.plotly_chart(
            fig_quantidade_estados,
            use_container_width=True)

    with coluna2:
        st.metric(
            'Média de Vendas por Mês',
            formata_numero(quantidade_mensal['Quantidade'].mean()))

        st.plotly_chart(
            fig_quantidade_mensal,
            use_container_width=True)

        st.plotly_chart(
            fig_quantidade_categorias,
            use_container_width=True)


with aba3:
    gtd_vendedores = st.number_input('Quantidade de Vendedores', min_value = 2, max_value = 10, value = 5)
    coluna1, coluna2 = st.columns(2)
    
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$ '))

        dados_receita = vendedores[['sum']].sort_values('sum', ascending = False).head(gtd_vendedores)

        fig_receita_vendedores = px.bar(
            dados_receita, 
            x = dados_receita.index,  # Nomes dos vendedores no eixo X
            y = 'sum',                # Valores da receita no eixo Y
            text_auto = True, 
            title = f'Top {gtd_vendedores} Vendedores por Receita'
        )
        st.plotly_chart(fig_receita_vendedores, use_container_width = True)
        
    with coluna2: 
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))

        dados_vendas = vendedores[['count']].sort_values('count', ascending = False).head(gtd_vendedores)

        fig_vendas_vendedores = px.bar(
            dados_vendas,
            x = dados_vendas.index,   # Nomes dos vendedores no eixo X
            y = 'count',              # Quantidade de vendas no eixo Y
            text_auto = True, 
            title = f'Top {gtd_vendedores} Vendedores por Quantidade de Vendas'
        )
        st.plotly_chart(fig_vendas_vendedores, use_container_width = True)
