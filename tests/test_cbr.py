import pytest
import pandas as pd
import cbrkit.sim
import cbrkit.sim.numbers
from cbr_updated import Cbr

# --- Fixture 1: Mock de todas as dependências de I/O ---

@pytest.fixture
def mock_cbr_io(mocker):
    """
    Mocka todas as dependências externas que a classe Cbr usa
    para ler e escrever arquivos durante o __init__.
    """
    
    # 1. Mock do pandas.read_csv
    # Simula um "arquivo CSV" sujo que a classe precisa limpar
    mock_df_sujo = pd.DataFrame({
        'segundaCartaHumano': ['10', 'NULL', '5'],
        'naipe': ['ESPADAS', 'OURO', 'COPAS'],
        'valor': [10, -20, 30]
    })
    mocker.patch('cbr_updated.pd.read_csv', return_value=mock_df_sujo)
    
    # 2. Mock do tempfile e os.remove (para não tocar no disco)
    # Precisamos mockar __enter__ para o 'with' statement
    mock_temp_file = mocker.MagicMock()
    mock_temp_file.__enter__.return_value = mocker.MagicMock(name="temp_file.csv")
    mocker.patch('cbr_updated.tempfile.NamedTemporaryFile', return_value=mock_temp_file)
    mocker.patch('cbr_updated.os.remove')
    
    # 3. Mock do cbrkit.loaders.file
    # Simula o cbrkit carregando os dados (retornamos um dict simples)
    mock_loaded_data = {
        1: {'id': 1, 'data': 'caso1'},
        2: {'id': 2, 'data': 'caso2'}
    }
    mocker.patch('cbr_updated.cbrkit.loaders.file', return_value=mock_loaded_data)
    
    # 4. Spy do pd.DataFrame.to_csv
    # Isso nos permite "espionar" o dataframe *depois* de limpo
    spy_to_csv = mocker.spy(pd.DataFrame, 'to_csv')
    
    return spy_to_csv, mock_loaded_data


def test_cbr_init_e_atualizarDataframe(mock_cbr_io, mocker):
    """
    Testa todo o pipeline do __init__ e atualizarDataframe:
    1. Lê o CSV (mockado)
    2. Limpa os dados
    3. Salva em arquivo temporário (mockado)
    4. Carrega no cbrkit (mockado)
    5. Define cbr.casos
    """
    spy_to_csv, mock_loaded_data = mock_cbr_io
    
    # Instanciar a classe (isso executa o __init__ e o atualizarDataframe)
    cbr = Cbr()
    
    # --- Verificações ---
    
    # 1. Verificamos se o CSV original foi lido
    pd.read_csv.assert_called_once()
    
    # 2. Verificamos se to_csv foi chamado (provando que a limpeza foi feita)
    spy_to_csv.assert_called_once()
    
    # 3. Inspecionamos o dataframe que foi "salvo" (o dataframe limpo)
    # O primeiro argumento de to_csv é 'self' (o DataFrame)
    cleaned_df = spy_to_csv.call_args[0][0]
    
    # 'segundaCartaHumano': 'NULL' virou 0
    assert cleaned_df['segundaCartaHumano'].iloc[1] == 0 
    # 'naipe': 'ESPADAS' virou '1'
    assert cleaned_df['naipe'].iloc[0] == '1'
    # 'valor': -20 virou 20 (apply(abs))
    assert cleaned_df['valor'].iloc[1] == 20 
    
    # 4. Verificamos se o cbrkit carregou o arquivo
    cbrkit.loaders.file.assert_called_once()
    
    # 5. Verificamos se o resultado foi salvo em cbr.casos
    assert cbr.casos == mock_loaded_data


# --- Fixture 2: Uma instância do CBR com o __init__ "desligado" ---

@pytest.fixture
def cbr_com_casos(mocker):
    """
    Cria uma instância de Cbr, mas "desliga" o complexo
    atualizarDataframe do __init__ para que possamos
    injetar nossos próprios cbr.casos manualmente.
    """
    
    # Impede o __init__ de tentar ler arquivos
    mocker.patch.object(Cbr, 'atualizarDataframe', return_value={})
    
    cbr = Cbr()
    
    # Criamos casos mockados que se parecem com os do cbrkit
    # (Eles devem ter um método .to_dict())
    mock_case_1 = mocker.MagicMock(to_dict=lambda: {'id': 1, 'numeric': 10, 'string': 'A'})
    mock_case_2 = mocker.MagicMock(to_dict=lambda: {'id': 2, 'numeric': 100, 'string': 'B'})
    mock_case_3 = mocker.MagicMock(to_dict=lambda: {'id': 3, 'numeric': 10, 'string': 'C'}) # Teste de Div/0
    mock_case_4 = mocker.MagicMock(to_dict=lambda: {'id': 4, 'numeric': 10, 'string': 'D'}) # Teste de Div/0

    cbr.casos = {
        1: mock_case_1,
        2: mock_case_2,
        3: mock_case_3,
        4: mock_case_4,
    }
    return cbr


def test_buscar_similares_filtra_por_score(cbr_com_casos, mocker):
    """
    Testa a lógica de filtragem da função buscarSimilares.
    Garante que ele filtra corretamente os resultados por score >= 0.8.
    """
    cbr = cbr_com_casos
    
    # 1. Simula a resposta do cbrkit.apply_query
    mock_result = mocker.MagicMock()
    mock_result.ranking = [1, 2, 3] # IDs dos casos
    mock_result.similarities = [0.95, 0.80, 0.79] # Scores
    
    mocker.patch('cbr_updated.apply_query', return_value=mock_result)
    
    # 2. Executa a função
    similares = cbr.buscarSimilares({'numeric': 10, 'string': 'A'})
    
    # 3. Verifica o resultado
    assert len(similares) == 2 # Deve descartar o 0.79
    assert similares[0]['id'] == 1
    assert similares[0]['_sim_score'] == 0.95
    assert similares[1]['id'] == 2
    assert similares[1]['_sim_score'] == 0.80


def test_buscar_similares_constroi_sims_dinamicos(cbr_com_casos, mocker):
    """
    Testa se a função constrói as funções de similaridade
    corretamente (linear para números, 1/0 para strings).
    """
    cbr = cbr_com_casos
    
    # 1. Mock do pd.DataFrame para controlar min/max
    # A query usa 'numeric' e 'string'
    mock_df = pd.DataFrame([
        {'numeric': 10, 'string': 'A'},
        {'numeric': 100, 'string': 'B'}
    ])
    mocker.patch('cbr_updated.pd.DataFrame', return_value=mock_df)
    
    # 2. "Espiona" a chamada para cbrkit.sim.attribute_value
    spy_attr_sim = mocker.spy(cbrkit.sim, 'attribute_value')
    spy_linear_sim = mocker.spy(cbrkit.sim.numbers, 'linear_interval')
    
    # 3. Mock do apply_query (não nos importamos com o resultado aqui)
    mock_result = mocker.MagicMock(ranking=[], similarities=[])
    mocker.patch('cbr_updated.apply_query', return_value=mock_result)
    
    # 4. Executa a função com uma query que usa ambas as colunas
    query = {'numeric': 50, 'string': 'A'}
    cbr.buscarSimilares(query)
    
    # 5. Verifica os "espiões"
    spy_attr_sim.assert_called_once()
    
    # Pega os argumentos que foram passados para o construtor
    kwargs = spy_attr_sim.call_args[1]
    attributos_sim = kwargs['attributes']
    
    # Garante que ele criou a sim. linear para 'numeric'
    spy_linear_sim.assert_called_once_with(10, 100) # (min, max)
    
    # Garante que ele criou a sim. lambda para 'string'
    assert attributos_sim['string']('A', 'A') == 1.0
    assert attributos_sim['string']('A', 'B') == 0.0


def test_buscar_similares_evita_divisao_por_zero(cbr_com_casos, mocker):
    """
    Testa o caso de borda onde (mx == mn) para uma coluna numérica,
    o que causaria uma divisão por zero se não fosse tratado.
    """
    cbr = cbr_com_casos
    
    # 1. Mock do pd.DataFrame onde min == max
    mock_df = pd.DataFrame([
        {'numeric': 10, 'string': 'C'},
        {'numeric': 10, 'string': 'D'}
    ])
    mocker.patch('cbr_updated.pd.DataFrame', return_value=mock_df)
    
    # 2. Espiões
    spy_attr_sim = mocker.spy(cbrkit.sim, 'attribute_value')
    spy_linear_sim = mocker.spy(cbrkit.sim.numbers, 'linear_interval')
    
    # 3. Mock do apply_query
    mock_result = mocker.MagicMock(ranking=[], similarities=[])
    mocker.patch('cbr_updated.apply_query', return_value=mock_result)
    
    # 4. Executa a função
    query = {'numeric': 10}
    cbr.buscarSimilares(query)
    
    # 5. Verifica os espiões
    # A sim. linear NÃO deve ser chamada, pois mx == mn
    spy_linear_sim.assert_not_called()
    
    # A função de similaridade deve ser a lambda de 1.0/0.0
    kwargs = spy_attr_sim.call_args[1]
    attributos_sim = kwargs['attributes']
    
    assert attributos_sim['numeric'](10, 10) == 1.0
    assert attributos_sim['numeric'](10, 5) == 0.0