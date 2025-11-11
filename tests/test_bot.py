import pytest
import pandas as pd

from bot import Bot, retornarPontosEnvido

mock_envido = {
    "3": 3,
    "2": 2,
    "1": 1,
    "12": 0,
    "11": 0,
    "10": 0,
    "7": 7,
    "6": 6,
    "5": 5,
    "4": 4
}

def test_retornar_pontos_envido_com_flor(mocker):
    """
    Testa se o envido é calculado corretamente quando o jogador tem uma flor.
    """
    carta1 = mocker.MagicMock()
    carta1.numero = 7
    carta1.retornarNaipe.return_value = 'ESPADAS'

    carta2 = mocker.MagicMock()
    carta2.numero = 6
    carta2.retornarNaipe.return_value = 'ESPADAS'

    carta3 = mocker.MagicMock()
    carta3.numero = 1
    carta3.retornarNaipe.return_value = 'ESPADAS'

    mocker.patch('bot.ENVIDO', mock_envido)

    mao = [carta1, carta2, carta3]

    assert retornarPontosEnvido(mao) == 33  # 7 + 6 + 20

def test_retornar_pontos_envido_tres_naipes(mocker):
    """
    Testa se o envido é calculado corretamente quando o jogador tem cartas de três naipes diferentes.
    """
    carta1 = mocker.MagicMock()
    carta1.numero = 3
    carta1.retornarNaipe.return_value = 'ESPADAS'

    carta2 = mocker.MagicMock()
    carta2.numero = 2
    carta2.retornarNaipe.return_value = 'OUROS'

    carta3 = mocker.MagicMock()
    carta3.numero = 1
    carta3.retornarNaipe.return_value = 'BASTOS'

    mocker.patch('bot.ENVIDO', mock_envido)

    mao = [carta1, carta2, carta3]

    assert retornarPontosEnvido(mao) == 3

def test_retornar_pontos_envido_duas_cartas_mesmo_naipe(mocker):
    """
    Testa se o envido é calculado corretamente quando o jogador tem duas cartas do mesmo naipe.
    """
    carta1 = mocker.MagicMock()
    carta1.numero = 7
    carta1.retornarNaipe.return_value = 'ESPADAS'

    carta2 = mocker.MagicMock()
    carta2.numero = 5
    carta2.retornarNaipe.return_value = 'ESPADAS'

    carta3 = mocker.MagicMock()
    carta3.numero = 12
    carta3.retornarNaipe.return_value = 'BASTOS'

    mocker.patch('bot.ENVIDO', mock_envido)

    mao = [carta1, carta2, carta3]

    assert retornarPontosEnvido(mao) == 32  # 7 + 5 + 20

@pytest.fixture
def mock_bot(mocker):
    """
    Cria um bot simulado para os testes. Mocka dependências externas (CBR e pandas.read_csv).
    """
    # 1. Mockar o pandas.read_csv (chamado no __init__)
    # Retorna um DataFrame mockado que suporta acesso .iloc[0]
    mock_row = mocker.MagicMock(name="mock_row_0")
    mock_df = mocker.MagicMock(name="mock_df", iloc=[mock_row])

    # Intercepta a chamada `pd.read.csv`
    mocker.patch('bot.pd.read_csv', return_value=mock_df)

    # 2. Mockar o CBR (chamado no __init__)
    mock_cbr = mocker.MagicMock(name="mock_cbr")
    mock_cbr.buscarSimilares.return_value = [] # Padrao: retorna lista vazia

    # 3. Mockar o helper 'retornarPontosEnvido'
    # Evita dependencia do teste anterior
    mocker.patch('bot.retornarPontosEnvido', return_value=30)

    # 4. Criar o bot com os mocks
    bot = Bot(nome="TestBot", cbr=mock_cbr)

    return bot, mock_cbr, mock_df

def test_bot_init(mock_bot):
    """
    Testa se o __init__ inicializa o estado corretamente.
    """
    bot, mock_cbr, _ = mock_bot

    assert bot.nome == "TestBot"
    assert bot.cbr == mock_cbr
    assert bot.pontos == 0
    assert bot.mao == []
    assert bot.flor == False
    assert bot.ja_respondeu['truco'] == False

def test_resetar(mock_bot):
    """
    Testa se o método resetar() reinicia o estado do bot corretamente.
    """
    bot, _, _ = mock_bot

    bot.pontos = 5
    bot.mao = [1, 2, 3]
    bot.flor = True
    bot.ja_respondeu['truco'] = True

    bot.resetar()

    assert bot.mao == []
    assert bot.flor == False
    assert bot.ja_respondeu['truco'] == False

def test_criar_mao_e_inicializar_registro(mock_bot, mocker):
    """
    Testa criarMao e inicializarRegistro.
    """
    bot, _, mock_df = mock_bot

    mock_carta1 = mocker.MagicMock()
    mock_carta2 = mocker.MagicMock()
    mock_carta3 = mocker.MagicMock()

    # Configura o retorno de classificarCarta
    mock_carta1.classificarCarta.return_value = (
        [52, 24, 1], # pontuacaoCartas
        ['Alta', 'Media', 'Baixa'] # maoRank
    )

    mock_carta1.retornarNaipe.return_value = 'ESPADAS'
    mock_carta2.retornarNaipe.return_value = 'ESPADAS'
    mock_carta3.retornarNaipe.return_value = 'ESPADAS'

    mock_baralho = mocker.MagicMock()
    mock_baralho.retirarCarta.side_effect = [mock_carta1, mock_carta2, mock_carta3]

    bot.criarMao(mock_baralho)

    assert bot.mao == [mock_carta1, mock_carta2, mock_carta3]
    assert bot.flor == True # Baseado nos naipes mockados
    assert bot.pontuacaoCartas == [52, 24, 1]
    assert bot.maoRank == ['Alta', 'Media', 'Baixa']
    assert bot.forcaMao == 77 # (52 + 24 + 1)
    
    # 5. Asserts (inicializarRegistro)
    # Verifica se o bot populou o DataFrame mockado
    assert bot.modeloRegistro.cartaAltaRobo == 52
    assert bot.modeloRegistro.cartaMediaRobo == 24
    assert bot.modeloRegistro.cartaBaixaRobo == 1
    assert bot.modeloRegistro.pontosEnvidoRobo == 30

def test_decisao_majoritaria_aceita(mock_bot, mocker):
    """
    Testa o método decisaoMajoritaria quando a maioria das decisões é 'aceitar'.
    """
    bot, mock_cbr, _ = mock_bot

    # 1. Mocks
    # Mock dos casos similares (2 'sim' [valor 2], 1 'não [valor 1])
    sim_cases = [
        { 'quemTruco': 2, 'quandoTruco': 1, },
        { 'quemTruco': 2, 'quandoTruco': 1, },
        { 'quemTruco': 1, 'quandoTruco': 1, },
    ]
    mock_cbr.buscarSimilares.return_value = sim_cases
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'idMao': 1})

    # 2. Execução
    # O bot está avaliando 'quemTruco', na rodada 1, e o valor de 'aceite', é 2
    aceitar = bot._decisaoMajoritariaPorRodada('quemTruco', 'quandoTruco', 1, 2)

    # 2 de 3 são 'aceitar' (valor 2), logo o bot deve aceitar
    assert aceitar == True

def test_decisao_majoritaria_recusa(mock_bot, mocker):
    """Testa o método decisaoMajoritaria quando a maioria das decisões é 'recusar'."""
    bot, mock_cbr, _ = mock_bot
    
    # 1. Mocks
    # 1 'sim' [valor 2], 2 'não' [valor 1]
    sim_cases = [
        {'quemTruco': 2, 'quandoTruco': 1},
        {'quemTruco': 1, 'quandoTruco': 1},
        {'quemTruco': 1, 'quandoTruco': 1},
    ]
    mock_cbr.buscarSimilares.return_value = sim_cases
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'idMao': 1})
    
    # 2. Execução
    aceitar = bot._decisaoMajoritariaPorRodada("quemTruco", "quandoTruco", 1, 2)
    
    # 1 de 3 não é > 50%
    assert aceitar == False

def test_avaliar_jogada_responde_truco(mock_bot, mocker):
    """
    Testa a máquina de estados 'avaliarJogada'
    Cenário: Humano pediu truco, bot precisa responder.
    """
    bot, _, mock_df = mock_bot
    
    # 1. Configuração do Estado
    # Mocka a decisão interna (o bot decide ACEITAR)
    mocker.patch.object(bot, 'avaliarAceitarTruco', return_value=True)
    
    # Mocka a decisão interna (o bot decide ACEITAR)
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={
        'quemTruco': 1, 
        'quandoTruco': 1
    })
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'quero'}
    assert bot.ja_respondeu['truco'] == True

def test_avaliar_jogada_decide_jogar_carta(mock_bot, mocker):
    """
    Testa a máquina de estados 'avaliarJogada'
    Cenário: Nenhuma aposta foi feita, bot decide jogar uma carta (fallback).
    """
    bot, mock_cbr, mock_df = mock_bot
    
    # 1. Configuração do Estado
    # Garante que o bot não queira fazer nenhuma aposta
    mocker.patch.object(bot, 'avaliarEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarRealEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarFaltaEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarTruco', return_value=False)
    mocker.patch.object(bot, 'avaliarRetruco', return_value=False)
    mocker.patch.object(bot, 'avaliarValeQuatro', return_value=False)
    
    # Garante que não há casos similares (fallback de jogar carta)
    mock_cbr.buscarSimilares.return_value = []
    
    # Mão do bot
    mock_carta_baixa = mocker.MagicMock()
    mock_carta_baixa.retornarPontosCarta.return_value = 2
    bot.mao = [mock_carta_baixa]
    bot.pontuacaoCartas = [2] # O bot joga a carta mais baixa (2)
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'jogar carta', 'carta': 2}