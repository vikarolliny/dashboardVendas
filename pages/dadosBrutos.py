import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Download realizado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

st.sidebar.title('Filtros')

regioes = [
    'Brasil',
    'Centro-Oeste',
    'Nordeste',
    'Norte',
    'Sudeste',
    'Sul'
]

regiao = st.sidebar.selectbox(
    'Selecione a Região',
    regioes
)

if regiao == 'Brasil':
    regiao_api = ''
else:
    regiao_api = regiao.lower()

todos_anos = st.sidebar.checkbox(
    'Dados de todos os anos',
    value=True
)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.number_input(
        'Selecione o Ano',
        min_value=2020,
        max_value=2023,
        value=2023
    )

query_string = {
    'regiao': regiao_api,
    'ano': ano
}

response = requests.get(
    url,
    params=query_string
)

dados = pd.DataFrame.from_dict(
    response.json()
)

dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'],
    format='%d/%m/%Y'
)

with st.expander('Colunas'):

    colunas = st.multiselect(
        'Selecione as colunas que deseja visualizar',
        options=list(dados.columns),
        default=list(dados.columns)
    )

with st.sidebar.expander('Nome do produto'):

    produtos = st.multiselect(
        'Selecione os produtos',
        options=sorted(dados['Produto'].unique())
    )

preco_minimo = float(dados['Preço'].min())
preco_maximo = float(dados['Preço'].max())

with st.sidebar.expander('Preço do produto'):

    preco = st.slider(
        'Selecione o intervalo de preço',
        min_value=preco_minimo,
        max_value=preco_maximo,
        value=(preco_minimo, preco_maximo)
    )

data_minima = dados['Data da Compra'].min().date()
data_maxima = dados['Data da Compra'].max().date()

with st.sidebar.expander('Data da compra'):

    data = st.date_input(
        'Selecione o período',
        value=(data_minima, data_maxima),
        min_value=data_minima,
        max_value=data_maxima,
        key='periodo_dados_brutos'
    )

with st.sidebar.expander('Vendedor'):

    vendedores = st.multiselect(
        'Selecione os vendedores',
        options=sorted(dados['Vendedor'].unique())
    )

with st.sidebar.expander('Local da compra'):

    locais = st.multiselect(
        'Selecione os locais da compra',
        options=sorted(dados['Local da compra'].unique())
    )

with st.sidebar.expander('Categoria do produto'):

    categorias = st.multiselect(
        'Selecione as categorias',
        options=sorted(dados['Categoria do Produto'].unique())
    )

dados_filtrados = dados.copy()

if produtos:
    dados_filtrados = dados_filtrados[
        dados_filtrados['Produto'].isin(produtos)
    ]

dados_filtrados = dados_filtrados[
    dados_filtrados['Preço'].between(
        preco[0],
        preco[1]
    )
]

if isinstance(data, (tuple, list)) and len(data) == 2:

    data_inicio = pd.Timestamp(data[0])
    data_fim = pd.Timestamp(data[1])

    dados_filtrados = dados_filtrados[
        dados_filtrados['Data da Compra'].between(
            data_inicio,
            data_fim
        )
    ]

if vendedores:
    dados_filtrados = dados_filtrados[
        dados_filtrados['Vendedor'].isin(vendedores)
    ]

if locais:
    dados_filtrados = dados_filtrados[
        dados_filtrados['Local da compra'].isin(locais)
    ]

if categorias:
    dados_filtrados = dados_filtrados[
        dados_filtrados['Categoria do Produto'].isin(categorias)
    ]

dados_filtrados = dados_filtrados[colunas]

st.subheader('Tabela de Dados')

st.dataframe(
    dados_filtrados,
    use_container_width=True
)

st.markdown(
    f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas '
    f'e :blue[{dados_filtrados.shape[1]}] colunas.'
)

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados')
    nome_arquivo = '.csv'
with coluna2:
    st.download_button(
        'Fazer o download da tabela em csv',
        data=converte_csv(dados_filtrados),
        file_name=nome_arquivo,
        mime='text/csv',
        on_click=mensagem_sucesso
    )
