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

def test_jogar_carta_sem_casos_similares(mock_bot, mocker):
    """
    Testa jogarCarta (Cenário 1): Nenhum caso similar encontrado (df.empty).
    O bot deve jogar a carta de menor valor.
    """
    bot, mock_cbr, mock_df = mock_bot
    
    # 1. Configurar Mão (2 cartas)
    mock_carta_baixa = mocker.MagicMock(name="Baixa")
    mock_carta_media = mocker.MagicMock(name="Media")
    bot.mao = [mock_carta_media, mock_carta_baixa]
    bot.pontuacaoCartas = [24, 2]
    bot.indices = [0, 1]
    
    # 2. Configurar Mocks
    # Mock para 'reset_index().iloc[0].to_dict()'
    mocker.patch.object(bot.modeloRegistro.reset_index().iloc[0], 'to_dict', return_value={})
    # CBR não retorna similares
    mock_cbr.buscarSimilares.return_value = []
    # Mock do pandas DataFrame para retornar df.empty == True
    mocker.patch('bot.pd.DataFrame', return_value=pd.DataFrame([])) 
    
    # 3. Execução
    carta_jogada = bot.jogarCarta()
    
    # 4. Asserts
    assert carta_jogada == mock_carta_baixa
    assert bot.mao == [mock_carta_media]
    assert bot.pontuacaoCartas == [24]
    assert bot.indices == [0]

def test_jogar_carta_com_caso_similar_match(mock_bot, mocker):
    """
    Testa jogarCarta (Cenário 2): Caso similar encontrado (caminho feliz).
    A carta mais comum (10) está na mão do bot.
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Mão (3 cartas)
    mock_carta_baixa = mocker.MagicMock(name="Baixa")
    mock_carta_media = mocker.MagicMock(name="Media")
    mock_carta_alta = mocker.MagicMock(name="Alta")
    bot.mao = [mock_carta_baixa, mock_carta_media, mock_carta_alta]
    bot.pontuacaoCartas = [2, 10, 52] # Pontos
    bot.indices = [0, 1, 2]
    
    # 2. Configurar Mocks
    mocker.patch.object(bot.modeloRegistro.reset_index().iloc[0], 'to_dict', return_value={})
    # CBR retorna casos
    mock_cbr.buscarSimilares.return_value = [{'primeiraCartaRobo': 10}]
    
    # Mockar o DataFrame e seu value_counts()
    mock_df = pd.DataFrame([{'primeiraCartaRobo': 10}])
    mocker.patch('bot.pd.DataFrame', return_value=mock_df)
    
    # 3. Execução
    carta_jogada = bot.jogarCarta()
    
    # 4. Asserts
    assert carta_jogada == mock_carta_media
    assert bot.mao == [mock_carta_baixa, mock_carta_alta]
    assert bot.pontuacaoCartas == [2, 52]
    assert bot.indices == [0, 1]

def test_jogar_carta_com_caso_similar_sem_match(mock_bot, mocker):
    """
    Testa jogarCarta (Cenário 3): Caso similar encontrado (fallback).
    A carta mais comum (40) não está na mão. Bot deve jogar a mais próxima (52).
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Mão (3 cartas)
    mock_carta_baixa = mocker.MagicMock(name="Baixa")
    mock_carta_media = mocker.MagicMock(name="Media")
    mock_carta_alta = mocker.MagicMock(name="Alta")
    bot.mao = [mock_carta_baixa, mock_carta_media, mock_carta_alta]
    bot.pontuacaoCartas = [2, 24, 52]
    bot.indices = [0, 1, 2]
    
    # 2. Configurar Mocks
    mocker.patch.object(bot.modeloRegistro.reset_index().iloc[0], 'to_dict', return_value={})
    # CBR retorna casos, a carta ideal é 40
    mock_cbr.buscarSimilares.return_value = [{'primeiraCartaRobo': 40}] 
    
    # Mockar o DataFrame e seu value_counts()
    mock_df = pd.DataFrame([{'primeiraCartaRobo': 40}])
    mocker.patch('bot.pd.DataFrame', return_value=mock_df)
    
    # 3. Execução
    carta_jogada = bot.jogarCarta()
    
    # 4. Asserts
    # A carta 40 não está na mão [2, 24, 52].
    # A mais próxima de 40 é 52 (abs(52-40)=12).
    assert carta_jogada == mock_carta_alta 
    assert bot.mao == [mock_carta_baixa, mock_carta_media]
    assert bot.pontuacaoCartas == [2, 24]

def test_avaliar_jogada_propoe_flor(mock_bot, mocker):
    """
    Testa avaliarJogada: Bot deve propor 'flor' na rodada 1.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = True
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={})
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'flor'}

def test_avaliar_jogada_propoe_envido(mock_bot, mocker):
    """
    Testa avaliarJogada: Bot não tem flor e decide propor 'envido'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = False
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={})
    
    # Mockar a decisão interna
    mocker.patch.object(bot, 'avaliarEnvido', return_value=True)
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'envido'}

def test_avaliar_jogada_responde_envido_nao_quero(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano pediu envido, bot decide 'não quero'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = False
    # Registro indica que humano (1) pediu envido
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemPediuEnvido': 1})
    
    # Mockar a decisão interna
    mocker.patch.object(bot, 'avaliarAceitarEnvido', return_value=False)
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'não quero'}
    assert bot.ja_respondeu['envido'] == True

def test_avaliar_envido_guarda_truco(mock_bot):
    """
    Testa a lógica de guarda de 'avaliarEnvido'.
    Não se pode cantar Envido se o Truco já foi cantado (quemTruco=2).
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado (Truco já foi cantado pelo bot)
    bot.modeloRegistro.iloc[0]["quemTruco"] = 2
    
    # 2. Execução
    # A função _decisaoMajoritaria nem deve ser chamada
    resultado = bot.avaliarEnvido(rodada=1)
    
    # 3. Assert
    assert resultado == False

def test_avaliar_retruco_guarda_sem_truco(mock_bot):
    """
    Testa a lógica de guarda de 'avaliarRetruco'.
    Bot não pode cantar Retruco se não foi trucado (quemTruco != 1).
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado (Ninguém trucou)
    bot.modeloRegistro.iloc[0]["quemTruco"] = 0 
    
    # 2. Execução
    resultado = bot.avaliarRetruco(rodada=1)
    
    # 3. Assert
    assert resultado == False

def test_checa_flor_falso(mock_bot, mocker):
    """Testa 'checaFlor' quando os naipes são diferentes."""
    bot, _, _ = mock_bot
    
    mock_carta_1 = mocker.MagicMock()
    mock_carta_1.retornarNaipe.return_value = "ESPADAS"
    mock_carta_2 = mocker.MagicMock()
    mock_carta_2.retornarNaipe.return_value = "COPAS"
    
    bot.mao = [mock_carta_1, mock_carta_2]
    
    assert bot.checaFlor() == False
    assert bot.flor == False

def test_checa_flor_mao_vazia_retorna_false(mock_bot):
    """Testa se 'checaFlor' retorna False com mão vazia."""
    bot, _, _ = mock_bot
    bot.mao = []
    
    assert bot.checaFlor() == False

def test_ajusta_indices_mao(mock_bot):
    """Testa o utilitário 'AjustaIndicesMao'."""
    bot, _, _ = mock_bot
    
    assert bot.AjustaIndicesMao(tam_mao=2) == [0, 1]
    assert bot.AjustaIndicesMao(tam_mao=1) == [0]

def test_avaliar_jogada_responde_contra_flor(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano canta 'Flor', bot decide cantar 'Contra-Flor'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = True # Bot também tem flor
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemFlor': 1}) # Humano (1) cantou flor
    
    # Mockar a decisão interna
    mocker.patch.object(bot, 'avaliarContraFlor', return_value=True) # Bot decide escalar
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'contra flor'}
    assert bot.ja_respondeu['contra flor'] == True

def test_avaliar_jogada_responde_contra_flor_resto(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano canta 'Contra-Flor', bot decide escalar para 'Contra-Flor e Resto'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = True
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemContraFlor': 1}) # Humano (1) cantou Contra-Flor
    
    # Mockar decisões
    mocker.patch.object(bot, 'avaliarContraFlorResto', return_value=True) # Bot decide ir pro 'Resto'
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'contra flor resto'}
    assert bot.ja_respondeu['contra flor resto'] == True

def test_avaliar_jogada_responde_contra_flor_aceita_sem_escalar(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano canta 'Contra-Flor', bot decide apenas aceitar ('Quero').
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    bot.flor = True
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemContraFlor': 1}) # Humano (1) cantou Contra-Flor
    
    # Mockar decisões
    mocker.patch.object(bot, 'avaliarContraFlorResto', return_value=False) # Bot NÃO quer 'Resto'
    mocker.patch.object(bot, 'avaliarContraFlor', return_value=True) # Bot aceita a Contra-Flor (diz 'Quero')
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    assert jogada == {'jogada': 'quero'}
    assert bot.ja_respondeu['contra flor resto'] == True

def test_avaliar_jogada_propoe_retruco(mock_bot, mocker):
    """
    Testa avaliarJogada: Bot foi 'trucado' (quemTruco=1) e decide propor 'Retruco'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    # Humano (1) pediu truco. Bot pulou a resposta (talvez aceitou antes).
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemTruco': 1}) 
    
    # Mockar decisões
    # Bot não vai propor 'truco' (já foi proposto)
    mocker.patch.object(bot, 'avaliarTruco', return_value=False) 
    # Bot decide propor 'retruco'
    mocker.patch.object(bot, 'avaliarRetruco', return_value=True) 
    
    # 2. Execução (na rodada 2, para pular a lógica de envido)
    jogada = bot.avaliarJogada(rodada=2)
    
    # 3. Assert
    assert jogada == {'jogada': 'retruco'}

def test_avaliar_jogada_ignora_aposta_ja_respondida(mock_bot, mocker):
    """
    Testa a lógica de guarda `ja_respondeu`.
    Bot não deve responder 'quero' ao truco se já respondeu.
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Estado
    bot.ja_respondeu['truco'] = True
    
    # O registro ainda mostra o pedido de truco do humano
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemTruco': 1, 'quandoTruco': 1})
    
    # Spy: Mockamos 'avaliarAceitarTruco' para garantir que não seja chamado
    spy_avaliar = mocker.patch.object(bot, 'avaliarAceitarTruco')
    
    # Configurar para cair no fallback de jogar carta
    mocker.patch.object(bot, 'avaliarEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarRealEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarFaltaEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarTruco', return_value=False)
    mocker.patch.object(bot, 'avaliarRetruco', return_value=False)
    mocker.patch.object(bot, 'avaliarValeQuatro', return_value=False)
    mock_cbr.buscarSimilares.return_value = []
    bot.pontuacaoCartas = [5]
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    spy_avaliar.assert_not_called() 
    assert jogada == {'jogada': 'jogar carta', 'carta': 5}

def test_avaliar_jogada_responde_vale_quatro(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano canta 'Vale Quatro', bot decide 'Quero'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    # Mockar a decisão interna
    mocker.patch.object(bot, 'avaliarValeQuatro', return_value=True) # Bot decide aceitar
    
    # Mockar o registro
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={
        'quemValeQuatro': 1, 
        'quandoValeQuatro': 2
    })
    
    # 2. Execução (na rodada 2 para pular envido)
    jogada = bot.avaliarJogada(rodada=2)
    
    # 3. Assert
    assert jogada == {'jogada': 'quero'}
    assert bot.ja_respondeu['vale_quatro'] == True

def test_avaliar_jogada_propoe_vale_quatro(mock_bot, mocker):
    """
    Testa avaliarJogada: Bot foi 'retrucado' (quemRetruco=1) e decide propor 'Vale Quatro'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemRetruco': 1})
    
    # Mockar decisões para forçar a avaliação do 'vale quatro'
    mocker.patch.object(bot, 'avaliarTruco', return_value=False)
    mocker.patch.object(bot, 'avaliarRetruco', return_value=False)
    mocker.patch.object(bot, 'avaliarValeQuatro', return_value=True) # Bot decide propor
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=2)
    
    # 3. Assert
    assert jogada == {'jogada': 'vale quatro'}

def test_jogar_carta_usa_coluna_segunda_rodada(mock_bot, mocker):
    """
    Testa jogarCarta: Verifica se o bot usa a coluna 'segundaCartaRobo'
    quando tem 2 cartas na mão (len(indices) == 2).
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Mão (2 cartas restantes)
    mock_carta_baixa = mocker.MagicMock(name="Baixa")
    mock_carta_media = mocker.MagicMock(name="Media")
    bot.mao = [mock_carta_baixa, mock_carta_media]
    bot.pontuacaoCartas = [2, 10]
    bot.indices = [0, 1]
    
    # 2. Configurar Mocks
    mocker.patch.object(bot.modeloRegistro.reset_index().iloc[0], 'to_dict', return_value={})
    
    # CBR retorna casos
    mock_cbr.buscarSimilares.return_value = [{'segundaCartaRobo': 10}]
    
    # Mockar o DataFrame e seu value_counts()
    mock_df = pd.DataFrame([{'segundaCartaRobo': 10}])
    mocker.patch('bot.pd.DataFrame', return_value=mock_df)
    
    # 3. Execução
    carta_jogada = bot.jogarCarta()
    
    # 4. Asserts
    assert carta_jogada == mock_carta_media
    assert bot.pontuacaoCartas == [2]
    assert bot.indices == [0]

def test_mostrar_mao(mock_bot, mocker, capsys):
    """
    Testa se 'mostrarMao' chama 'printarCarta' corretamente para cada carta.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Mão
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    bot.mao = [mock_carta_1, mock_carta_2]
    
    # 2. Execução
    bot.mostrarMao()
    
    # 3. Asserts
    mock_carta_1.printarCarta.assert_called_with(0)
    mock_carta_2.printarCarta.assert_called_with(1)

def test_jogar_carta_usa_coluna_terceira_rodada(mock_bot, mocker):
    """
    Testa jogarCarta: Verifica se o bot usa a coluna 'terceiraCartaRobo'
    quando tem 1 carta na mão (len(indices) == 1).
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Mão (1 carta restante)
    mock_carta_alta = mocker.MagicMock(name="Alta")
    bot.mao = [mock_carta_alta]
    bot.pontuacaoCartas = [52]
    bot.indices = [0]
    
    # 2. Configurar Mocks
    mocker.patch.object(bot.modeloRegistro.reset_index().iloc[0], 'to_dict', return_value={})
    
    # CBR retorna casos
    mock_cbr.buscarSimilares.return_value = [{'terceiraCartaRobo': 52}]
    
    # Mockar o DataFrame e seu value_counts()
    mock_df = pd.DataFrame([{'terceiraCartaRobo': 52}])
    mocker.patch('bot.pd.DataFrame', return_value=mock_df)
    
    # 3. Execução
    carta_jogada = bot.jogarCarta()
    
    # 4. Asserts
    assert carta_jogada == mock_carta_alta
    assert bot.pontuacaoCartas == []
    assert bot.mao == []
    assert bot.indices == None

def test_avaliar_real_envido_guarda_truco(mock_bot):
    """
    Testa a lógica de guarda de 'avaliarRealEnvido'.
    Não se pode cantar Real Envido se o Truco já foi cantado (quemTruco=2).
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado (Truco já foi cantado pelo bot)
    bot.modeloRegistro.__getitem__.return_value = 2
    
    # 2. Execução
    resultado = bot.avaliarRealEnvido(rodada=1)
    
    # 3. Assert
    assert resultado == False

def test_avaliar_aceitar_envido_guarda_sem_pedido(mock_bot):
    """
    Testa a lógica de guarda de 'avaliarAceitarEnvido'.
    Não se pode aceitar Envido se ninguém o cantou (quemPediuEnvido=0).
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado (Ninguém pediu Envido)
    bot.modeloRegistro.iloc[0].__getitem__.return_value = 0
    
    # 2. Execução
    resultado = bot.avaliarAceitarEnvido(rodada=1)
    
    # 3. Assert
    assert resultado == False

def test_avaliar_jogada_responde_retruco(mock_bot, mocker):
    """
    Testa avaliarJogada: Humano canta 'Retruco', bot decide 'Quero'.
    """
    bot, _, _ = mock_bot
    
    # 1. Configurar Estado
    # Mockar a decisão interna
    mocker.patch.object(bot, 'avaliarRetruco', return_value=True) # Bot decide aceitar
    
    # Mockar o registro
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={
        'quemRetruco': 1, 
        'quandoRetruco': 2
    })
    
    # 2. Execução (na rodada 2 para pular envido)
    jogada = bot.avaliarJogada(rodada=2)
    
    # 3. Assert
    assert jogada == {'jogada': 'quero'}
    assert bot.ja_respondeu['retruco'] == True

def test_avaliar_jogada_ignora_aposta_ja_respondida(mock_bot, mocker):
    """
    Testa a lógica de guarda `ja_respondeu`.
    O bot não deve re-responder ao 'truco' se já o fez.
    """
    bot, mock_cbr, _ = mock_bot
    
    # 1. Configurar Estado
    bot.ja_respondeu['truco'] = True # O bot JÁ RESPONDEU ao truco
    
    # O registro ainda mostra o pedido de truco do humano
    mocker.patch.object(bot, '_obterRegistroUtil', return_value={'quemTruco': 1, 'quandoTruco': 1})
    
    # Spy: Mockamos 'avaliarAceitarTruco' para garantir que não seja chamado
    spy_avaliar = mocker.patch.object(bot, 'avaliarAceitarTruco')
    
    # Configurar para cair no fallback de jogar carta (pular apostas de envido/flor)
    bot.flor = False
    mocker.patch.object(bot, 'avaliarEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarRealEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarFaltaEnvido', return_value=False)
    mocker.patch.object(bot, 'avaliarTruco', return_value=False)
    mocker.patch.object(bot, 'avaliarRetruco', return_value=False)
    mocker.patch.object(bot, 'avaliarValeQuatro', return_value=False)
    mock_cbr.buscarSimilares.return_value = []
    bot.pontuacaoCartas = [5]
    
    # 2. Execução
    jogada = bot.avaliarJogada(rodada=1)
    
    # 3. Assert
    spy_avaliar.assert_not_called() 
    assert jogada == {'jogada': 'jogar carta', 'carta': 5}