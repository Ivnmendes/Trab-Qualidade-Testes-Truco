import pytest
from jogador import Jogador

@pytest.fixture
def jogador():
    """Fixture para criar uma instância de Jogador para os testes."""
    return Jogador("Teste")

def test_jogador_init(jogador):
    """
    Testa se o Jogador é inicializado corretamente.
    """
    assert jogador.nome == "Teste"
    assert jogador.mao == []
    assert jogador.pontos == 0
    assert jogador.rodadas == 0
    assert jogador.envido == 0
    assert jogador.primeiro is False
    assert jogador.ultimo is False
    assert jogador.flor is False
    assert jogador.pediuTruco is False

def test_criar_mao(jogador, mocker):
    """
    Testa se criarMao chama 'baralho.retirarCarta()' três vezes e adiciona as cartas à mão do jogador.
    """

    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_baralho = mocker.MagicMock()

    mock_baralho.retirarCarta.side_effect = [mock_carta_1, mock_carta_2, mock_carta_3]

    jogador.criarMao(mock_baralho)

    assert mock_baralho.retirarCarta.call_count == 3
    assert len(jogador.mao) == 3
    assert jogador.mao == [mock_carta_1, mock_carta_2, mock_carta_3]

def test_jogar_carta(jogador, mocker):
    """
    Testa se jogarCarta remove e retorna a carta correta da mão do jogador.
    """
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    carta_jogada = jogador.jogarCarta(1)

    assert carta_jogada == mock_carta_2
    assert len(jogador.mao) == 2
    assert jogador.mao == [mock_carta_1, mock_carta_3]

def test_resetar(jogador, mocker):
    """
    Testa se resetar limpa a mão do jogador e redefine flor para False.
    """
    mock_carta = mocker.MagicMock()
    jogador.mao = [mock_carta, mock_carta, mock_carta]
    jogador.flor = True

    jogador.resetar()

    assert jogador.mao == []
    assert jogador.flor is False

def test_checa_flor_true(jogador, mocker):
    """
    Testa se checaFlor retorna True quando todas as cartas na mão têm o mesmo naipe.
    """
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_carta_1.retornarNaipe.return_value = 'ESPADAS'
    mock_carta_2.retornarNaipe.return_value = 'ESPADAS'
    mock_carta_3.retornarNaipe.return_value = 'ESPADAS'

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    assert jogador.checaFlor() is True

def test_checa_flor_false(jogador, mocker):
    """
    Testa se checaFlor retorna False quando as cartas na mão têm naipes diferentes.
    """
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_carta_1.retornarNaipe.return_value = 'ESPADAS'
    mock_carta_2.retornarNaipe.return_value = 'COPAS'
    mock_carta_3.retornarNaipe.return_value = 'ESPADAS'

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    assert jogador.checaFlor() is False

def test_checa_flor_mao_vazia(jogador):
    """
    Testa se checaFlor retorna False quando a mão do jogador está vazia.
    """
    jogador.mao = []

    assert jogador.checaFlor() is False

def test_mostrar_mao(jogador, mocker, capsys):
    """
    Testa se mostrarMao chama printarCarta para cada carta na mão do jogador.
    """
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    jogador.mostrarMao()

    mock_carta_1.printarCarta.assert_called_once_with(0)
    mock_carta_2.printarCarta.assert_called_once_with(1)
    mock_carta_3.printarCarta.assert_called_once_with(2)

def test_mostrar_mao_vazia(jogador, capsys):
    """
    Testa se mostrarMao não lança erro quando a mão do jogador está vazia.
    """
    jogador.mao = []

    jogador.mostrarMao()

    captured = capsys.readouterr()
    assert captured.out == ""

def test_mostrar_opcoes_nao_pediu_truco(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes exibe a opção Truco quando pediuTruco é False.
    """
    jogador.pediuTruco = False
    mock_carta = mocker.MagicMock()
    jogador.mao = [mock_carta, mock_carta, mock_carta]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[4] Truco' in captured.out

def test_mostrar_opcoes_pediu_truco(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes não exibe a opção Truco quando pediuTruco é True.
    """
    jogador.pediuTruco = True
    mock_carta = mocker.MagicMock()
    jogador.mao = [mock_carta, mock_carta, mock_carta]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[4] Truco' not in captured.out

def test_mostrar_opcoes_flor_disponivel(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes exibe a opção Flor quando aplicável.
    """
    jogador.flor = False
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_carta_1.retornarNaipe.return_value = 'OUROS'
    mock_carta_2.retornarNaipe.return_value = 'OUROS'
    mock_carta_3.retornarNaipe.return_value = 'OUROS'

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[5] Flor' in captured.out
    assert '[5] Envido' not in captured.out
    assert '[6] Real Envido' not in captured.out
    assert '[7] Falta Envido' not in captured.out
    assert jogador.flor is True

def test_mostrar_opcoes_flor_indisponivel(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes não exibe a opção Flor quando não aplicável.
    """
    jogador.flor = False
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_carta_1.retornarNaipe.return_value = 'PAUS'
    mock_carta_2.retornarNaipe.return_value = 'COPAS'
    mock_carta_3.retornarNaipe.return_value = 'OUROS'

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[5] Flor' not in captured.out

def test_mostrar_opcoes_nao_mostra_flor_duas_vezes(jogador, mocker, capsys):
    """
    Testa para verificar se o jogo permite pedir Flor mais de uma vez
    """
    # 1. Configurar uma mão com flor
    mock_carta_1 = mocker.MagicMock(retornarNaipe=lambda: 'OUROS')
    mock_carta_2 = mocker.MagicMock(retornarNaipe=lambda: 'OUROS')
    mock_carta_3 = mocker.MagicMock(retornarNaipe=lambda: 'OUROS')
    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    # 2. Chamar a primeira vez (define jogador.flor = True)
    jogador.mostrarOpcoes()
    captured1 = capsys.readouterr()
    assert '[5] Flor' in captured1.out

    # 3. Chamar a segunda vez
    jogador.mostrarOpcoes()
    captured2 = capsys.readouterr()

    # 4. A opção não deve aparecer na segunda vez
    assert '[5] Flor' not in captured2.out

def test_mostrar_opcoes_envido(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes exibe as opções de Envido quando a mão tem 3 cartas.
    """
    mock_carta_1 = mocker.MagicMock()
    mock_carta_2 = mocker.MagicMock()
    mock_carta_3 = mocker.MagicMock()

    mock_carta_1.retornarNaipe.return_value = 'PAUS'
    mock_carta_2.retornarNaipe.return_value = 'COPAS'
    mock_carta_3.retornarNaipe.return_value = 'OUROS'

    jogador.mao = [mock_carta_1, mock_carta_2, mock_carta_3]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[5] Envido' in captured.out
    assert '[6] Real Envido' in captured.out
    assert '[7] Falta Envido' in captured.out

def test_mostrar_opcoes_mao_incompleta(jogador, mocker, capsys):
    """
    Testa se mostrarOpcoes não exibe opções de Envido quando a mão tem menos de 3 cartas.
    """
    mock_carta = mocker.MagicMock()
    jogador.mao = [mock_carta, mock_carta]

    jogador.mostrarOpcoes()

    captured = capsys.readouterr()
    assert '[5] Envido' not in captured.out
    assert '[6] Real Envido' not in captured.out
    assert '[7] Falta Envido' not in captured.out