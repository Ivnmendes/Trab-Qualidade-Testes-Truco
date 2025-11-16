import pytest
from jogo import Jogo

@pytest.fixture
def jogo():
    """Fornece uma instância limpa de Jogo() para cada teste."""
    return Jogo()

MOCK_ENVIDO = {
    "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2, "1": 1,
    "12": 0, "11": 0, "10": 0
}

def test_resetar_jogo(jogo):
    """
    Testa se 'resetarJogo' (chamado pelo __init__) define os padrões corretamente.
    """
    jogo.pontos_mao = 5
    jogo.truco['quemPediu'] = 1
    jogo.rodada_atual = 3
    jogo.encerrar_mao = True

    jogo.resetarJogo()

    assert jogo.pontos_mao == 1
    assert jogo.truco['quemPediu'] == 0
    assert jogo.truco['aceito'] is None
    assert jogo.rodada_atual == -1
    assert jogo.encerrar_mao == False
    assert jogo.pontos_maximos == 12

def test_criar_jogador(jogo, mocker):
    """
    Testa se 'criarJogador' instancia um Jogador e chama 'criarMao'.
    """
    mock_baralho = mocker.MagicMock(name="Baralho")
    mock_jogador_class = mocker.patch('jogo.Jogador')
    mock_jogador_instance = mocker.MagicMock(name="JogadorInstance")
    mock_jogador_class.return_value = mock_jogador_instance

    jogador = jogo.criarJogador("Humano", mock_baralho)

    mock_jogador_class.assert_called_once_with("Humano")
    mock_jogador_instance.criarMao.assert_called_once_with(mock_baralho)
    assert jogador == mock_jogador_instance

def test_criar_bot(jogo, mocker):
    """
    Testa se 'criarBot' instancia um Bot e chama 'criarMao'.
    """
    mock_baralho = mocker.MagicMock(name="Baralho")
    mock_cbr = mocker.MagicMock(name="CBR")
    mock_bot_class = mocker.patch('jogo.Bot')
    mock_bot_instance = mocker.MagicMock(name="BotInstance")
    mock_bot_class.return_value = mock_bot_instance

    bot = jogo.criarBot("IA", mock_baralho, mock_cbr)

    mock_bot_class.assert_called_once_with("IA", mock_cbr)
    mock_bot_instance.criarMao.assert_called_once_with(mock_baralho)
    assert bot == mock_bot_instance

def test_verificar_carta_vencedora(jogo, mocker):
    """
    Testa a lógica de comparação de 'verificarCartaVencedora'.
    """
    carta_baixa = mocker.MagicMock()
    carta_baixa.retornarPontosCarta.return_value = 10
    
    carta_alta = mocker.MagicMock()
    carta_alta.retornarPontosCarta.return_value = 52
    
    assert jogo.verificarCartaVencedora(carta_baixa, carta_alta) == carta_alta
    assert jogo.verificarCartaVencedora(carta_alta, carta_baixa) == carta_alta
    
    carta_baixa.retornarPontosCarta.return_value = 52
    assert jogo.verificarCartaVencedora(carta_baixa, carta_alta) == "Empate"

def test_retornar_pontos_envido(jogo, mocker):
    """
    Testa o cálculo de envido (lógica duplicada do bot.py).
    """
    mocker.patch('jogo.ENVIDO', MOCK_ENVIDO)
    
    c1 = mocker.MagicMock(numero="7", retornarNaipe=lambda: "OUROS")
    c2 = mocker.MagicMock(numero="6", retornarNaipe=lambda: "OUROS")
    c3 = mocker.MagicMock(numero="1", retornarNaipe=lambda: "OUROS")
    assert jogo.retornarPontosEnvido([c1, c2, c3]) == 33

    c1 = mocker.MagicMock(numero="12", retornarNaipe=lambda: "OUROS")
    c2 = mocker.MagicMock(numero="11", retornarNaipe=lambda: "ESPADAS")
    c3 = mocker.MagicMock(numero="10", retornarNaipe=lambda: "COPAS")
    assert jogo.retornarPontosEnvido([c1, c2, c3]) == 0

def test_aceitar_pedido_truco_aceito(jogo):
    """
    Testa aceitar o 'truco' (primeiro item da lista).
    """
    jogo.truco['quemPediu'] = 1
    jogo.truco['aceito'] = None
    
    resultado = jogo.aceitar_pedido(quem=2, rodada=1, aceito=True)
    
    assert resultado == True
    assert jogo.truco['aceito'] == True
    assert jogo.truco['quandoPediu'] == 1

def test_aceitar_pedido_envido_recusado(jogo):
    """
    Testa recusar o 'envido'.
    """
    jogo.envido['quemPediu'] = 2
    jogo.envido['aceito'] = None
    
    resultado = jogo.aceitar_pedido(quem=1, rodada=1, aceito=False)
    
    assert resultado == True
    assert jogo.envido['aceito'] == False

def test_aceitar_pedido_prioridade(jogo):
    """
    Testa se o método aceita o *primeiro* pedido pendente da lista (truco).
    """
    jogo.truco['quemPediu'] = 1
    jogo.truco['aceito'] = None
    jogo.envido['quemPediu'] = 1
    jogo.envido['aceito'] = None
    
    resultado = jogo.aceitar_pedido(quem=2, rodada=1, aceito=True)
    
    assert jogo.truco['aceito'] == True
    assert jogo.envido['aceito'] == None
    assert resultado == True

def test_aceitar_pedido_nenhum_pendente(jogo, capsys):
    """
    Testa o comportamento quando não há pedidos pendentes.
    """
    resultado = jogo.aceitar_pedido(quem=1, rodada=1, aceito=True)
    captured = capsys.readouterr()

    assert resultado == False
    assert "Não há pedido pendente para aceitar." in captured.out

def test_trocar_jogador_mao(jogo, mocker):
    """
    Testa a lógica de 'trocarJogadorMao'.
    """
    mock_j1 = mocker.MagicMock(primeiro=True)
    mock_j2 = mocker.MagicMock(primeiro=False)

    jogo.jogador_mao = 1
    
    jogo.trocarJogadorMao(mock_j1, mock_j2)

    assert mock_j1.primeiro == False 
    assert mock_j2.primeiro == True
    
    jogo.trocarJogadorMao(mock_j1, mock_j2)
    
    assert mock_j1.primeiro == True 
    assert mock_j2.primeiro == False 