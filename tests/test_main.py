import builtins
import pytest
import updated_main as partida
from carta import Carta
from jogo import Jogo
from jogador import Jogador
from baralho import Baralho
from cbr_updated import Cbr
from bot import Bot

def test_atualizar_conhecimento_truco(mocker):
    """
    Testa se a jogada 'truco' chama 'atualizarRegistro' com os parâmetros corretos
    quando não é uma negação.
    """
    mock_bot = mocker.MagicMock()
    
    partida.atualizar_conhecimento_jogada_especial(
        jogada="truco",
        jogador2=mock_bot,
        rodada=1,
        quem=1,
        negou=False
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ["quemTruco", "quandoTruco"],
        [1, 1]
    )

def test_atualizar_conhecimento_truco_negado(mocker):
    """
    Testa se a jogada 'truco' (negada) chama 'atualizarRegistro' corretamente.
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="truco",
        jogador2=mock_bot,
        rodada=1,
        quem=2,
        negou=True
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ["quemNegouTruco"], 
        [2]                 
    )

def test_atualizar_conhecimento_vale_quatro(mocker):
    """
    Testa a jogada 'vale quatro' (não negada).
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="vale quatro",
        jogador2=mock_bot,
        rodada=3,
        quem=1, 
        negou=False
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ["quemValeQuatro", "quandoValeQuatro"],
        [1, 3]
    )

def test_atualizar_conhecimento_envido(mocker):
    """
    Testa a jogada 'envido' (não negada).
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="envido",
        jogador2=mock_bot,
        rodada=1,
        quem=2, 
        negou=False
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ["quemPediuEnvido"],
        [2]
    )

def test_atualizar_conhecimento_falta_envido_negado(mocker):
    """
    Testa a jogada 'falta envido' (negada).
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="falta envido",
        jogador2=mock_bot,
        rodada=1,
        quem=1, 
        negou=True
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ["quemNegouFaltaEnvido"],
        [1]
    )

def test_atualizar_conhecimento_flor(mocker):
    """
    Testa a jogada 'flor' (não negada).
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="flor",
        jogador2=mock_bot,
        rodada=1,
        quem=1, 
        negou=False
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ['quemFlor'],
        [1]
    )

def test_atualizar_conhecimento_contra_flor_resto_negado(mocker):
    """
    Testa a jogada 'contra flor resto' (negada).
    """
    mock_bot = mocker.MagicMock()

    partida.atualizar_conhecimento_jogada_especial(
        jogada="contra flor resto",
        jogador2=mock_bot,
        rodada=1,
        quem=2, 
        negou=True
    )
    
    mock_bot.atualizarRegistro.assert_called_once_with(
        ['quemNegouFlor'],
        [2]
    )

def test_confrontar_envido_j1_ganha(mocker):
    """
    Testa 'confrontarEnvido' onde J1 (Humano) tem mais pontos.
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_j1 = mocker.MagicMock()
    mock_j2 = mocker.MagicMock()

    mocker.patch.object(mock_jogo, 'retornarPontosEnvido', side_effect=[30, 27])
    mock_jogo.pontos_j1 = 0

    partida.confrontarEnvido(mock_jogo, 'envido', mock_j1, mock_j2)

    assert mock_jogo.pontos_j1 == 2
    mock_j2.atualizarRegistro.assert_called_with(['pontosEnvidoHumano'], [30])

def test_confrontar_envido_j2_ganha_real(mocker):
    """
    Testa 'confrontarEnvido' onde J2 (Bot) ganha um 'real envido'.
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_j1 = mocker.MagicMock()
    mock_j2 = mocker.MagicMock()

    mocker.patch.object(mock_jogo, 'retornarPontosEnvido', side_effect=[20, 25])
    mock_jogo.pontos_j2 = 0
    
    partida.confrontarEnvido(mock_jogo, 'real envido', mock_j1, mock_j2)
    
    assert mock_jogo.pontos_j2 == 6

def test_confrontar_envido_empate_ganha_mao(mocker):
    """
    Testa 'confrontarEnvido' onde há empate, e J1 é o 'jogador_mao'.
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_j1 = mocker.MagicMock()
    mock_j2 = mocker.MagicMock()

    mocker.patch.object(mock_jogo, 'retornarPontosEnvido', side_effect=[30, 30])
    mock_jogo.pontos_j1 = 0
    mock_jogo.jogador_mao = 1
    
    partida.confrontarEnvido(mock_jogo, 'envido', mock_j1, mock_j2)
    
    assert mock_jogo.pontos_j1 == 2

def test_confrontar_envido_falta_envido(mocker):
    """
    Testa 'confrontarEnvido' para 'falta envido', calculando pontos restantes.
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_j1 = mocker.MagicMock()
    mock_j2 = mocker.MagicMock()

    mocker.patch.object(mock_jogo, 'retornarPontosEnvido', side_effect=[30, 27])

    mock_jogo.pontos_maximos = 12
    mock_jogo.pontos_j1 = 5
    mock_jogo.pontos_j2 = 3
    
    partida.confrontarEnvido(mock_jogo, 'falta envido', mock_j1, mock_j2)
    
    assert mock_jogo.pontos_j1 == 5 + 7

def test_distribuir_pontos_j1_encerra_mao(mocker, capsys):
    """
    Testa a distribuição de pontos para J1, com encerramento de mão (ex: truco negado).
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.pontos_j1 = 0
    
    partida.distribuir_pontos(mock_jogo, quem=1, pontos=2, encerrar_mao=True)
    
    assert mock_jogo.pontos_j1 == 2
    assert mock_jogo.encerrar_mao == True
    assert mock_jogo.truco_negado == True
    
    captured = capsys.readouterr()
    assert "Distribuindo 2 para o jogador 1" in captured.out

def test_distribuir_pontos_j2_sem_encerrar(mocker, capsys):
    """
    Testa a distribuição de pontos para J2, sem encerrar a mão (ex: envido negado).
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.pontos_j2 = 5
    mock_jogo.encerrar_mao = False
    mock_jogo.truco_negado = False
    
    partida.distribuir_pontos(mock_jogo, quem=2, pontos=1, encerrar_mao=False)
    
    assert mock_jogo.pontos_j2 == 6
    assert mock_jogo.encerrar_mao is not True
    assert mock_jogo.truco_negado is not True

def test_inverter_jogador():
    """Testa a lógica de 'inverter_jogador'."""
    assert partida.inverter_jogador(1) == 2
    assert partida.inverter_jogador(2) == 1

@pytest.fixture
def mock_jogo_para_verificar(mocker):
    """
    Fixture que cria um mock de 'Jogo' com valores padrão 
    para os testes de 'verificar_ganhador'.
    """
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.pontos_j1 = 0
    mock_jogo.pontos_j2 = 0
    mock_jogo.pontos_mao = 1
    mock_jogo.pontos_maximos = 12
    mock_jogo.encerrar_mao = False
    mock_jogo.encerrar_jogo = False
    mock_jogo.truco_negado = False
    mock_jogo.jogador_mao = 1

    mock_jogo.rodadas_vencedor = [0, 0, 0] 
    return mock_jogo

def test_verificar_ganhador_j1_ganha_simples(mock_jogo_para_verificar):
    """
    Testa a vitória simples: J1 ganha as duas primeiras rodadas.
    """
    jogo = mock_jogo_para_verificar
    jogo.rodadas_vencedor = [1, 1, 0]
    jogo.rodada_atual = 2

    partida.verificar_ganhador(jogo)

    assert jogo.pontos_j1 == 1
    assert jogo.encerrar_mao == True
    assert jogo.jogador_mao == 2

def test_verificar_ganhador_j2_ganha_simples(mock_jogo_para_verificar):
    """
    Testa a vitória simples: J2 ganha a R1 e R3.
    """
    jogo = mock_jogo_para_verificar
    jogo.rodadas_vencedor = [2, 1, 2]
    jogo.rodada_atual = 3
    
    partida.verificar_ganhador(jogo)
    
    assert jogo.pontos_j2 == 1
    assert jogo.encerrar_mao == True
    assert jogo.jogador_mao == 2

def test_verificar_ganhador_empate_r1_j1_ganha_r2(mock_jogo_para_verificar):
    """
    Testa a regra: Empate R1, J1 ganha R2. J1 vence a mão.
    """
    jogo = mock_jogo_para_verificar
    jogo.rodadas_vencedor = [3, 1, 0]
    jogo.rodada_atual = 2

    partida.verificar_ganhador(jogo)

    assert jogo.pontos_j1 == 1
    assert jogo.encerrar_mao == True

def test_verificar_ganhador_empate_r2_j2_ganha_r1(mock_jogo_para_verificar):
    """
    Testa a regra: J2 ganha R1, Empate R2. J2 vence a mão.
    """
    jogo = mock_jogo_para_verificar
    jogo.rodadas_vencedor = [2, 3, 0]
    jogo.rodada_atual = 2

    partida.verificar_ganhador(jogo)

    assert jogo.pontos_j2 == 1
    assert jogo.encerrar_mao == True

def test_verificar_ganhador_empate_r1_r2_j1_ganha_r3(mock_jogo_para_verificar):
    """
    Testa a regra: Empate R1, Empate R2, J1 ganha R3. J1 vence a mão.
    """
    jogo = mock_jogo_para_verificar
    jogo.rodadas_vencedor = [3, 3, 1]
    jogo.rodada_atual = 3

    partida.verificar_ganhador(jogo)

    assert jogo.pontos_j1 == 1
    assert jogo.encerrar_mao == True

def test_verificar_ganhador_nao_encerra_com_truco_negado(mock_jogo_para_verificar):
    """
    Testa se a lógica de contagem de rodadas é ignorada se 'truco_negado' for True.
    """
    jogo = mock_jogo_para_verificar
    jogo.truco_negado = True
    jogo.rodadas_vencedor = [1, 1, 0]
    jogo.rodada_atual = 2
    
    partida.verificar_ganhador(jogo)

    assert jogo.pontos_j1 == 0
    assert jogo.encerrar_mao == False

    assert jogo.jogador_mao == 1

def test_verificar_ganhador_encerra_jogo(mock_jogo_para_verificar):
    """
    Testa se a mão encerra o jogo quando os pontos máximos são atingidos.
    """
    jogo = mock_jogo_para_verificar
    jogo.pontos_j1 = 10
    jogo.pontos_mao = 2
    jogo.rodadas_vencedor = [1, 1, 0]
    jogo.rodada_atual = 2
    
    partida.verificar_ganhador(jogo)
    
    assert jogo.pontos_j1 == 12
    assert jogo.encerrar_mao == True
    assert jogo.encerrar_jogo == True

@pytest.fixture
def mocks_escalonamento(mocker):
    """Fixture que cria mocks de Jogo, Jogador 1 (Humano) e Jogador 2 (Bot)."""
    mock_jogo = mocker.MagicMock()
    mock_jogo.pontos_mao = 1
    mock_jogo.rodada_atual = 1
    mock_jogo.pontos.maximos = 12
    
    mock_j1 = mocker.MagicMock(nome="Humano")
    mock_j2 = mocker.MagicMock(nome="Bot")

    mocker.patch('updated_main.atualizar_conhecimento_jogada_especial')
    
    return mock_jogo, mock_j1, mock_j2


def test_escalonamento_truco_bot_chama_humano_aceita(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Bot (2) chama TRUCO, Humano (1) aceita.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento

    mocker.patch('builtins.input', return_value='s')

    resultado = partida.escalonamento(
        etapa=0,
        quem_chamou=2,
        jogador1=mock_j1,
        jogador2=mock_j2,
        jogo=mock_jogo,
        escalonamento_tipo="truco"
    )

    assert resultado == {"jogada": "truco", "resultado": "quero"}
    assert mock_jogo.pontos_mao == 2
    
    captured = capsys.readouterr()
    assert "Bot chamou truco!" in captured.out

def test_escalonamento_truco_bot_chama_humano_recusa(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Bot (2) chama TRUCO, Humano (1) recusa.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    mocker.patch('builtins.input', return_value='n')

    resultado = partida.escalonamento(
        etapa=0, quem_chamou=2, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="truco"
    )
    
    assert resultado == {
        "jogada": "truco", 
        "resultado": "não quero", 
        "quem_negou": 1, 
        "pontos": 1 
    }
    assert mock_jogo.pontos_mao == 1

def test_escalonamento_truco_bot_chama_humano_aumenta_bot_aceita(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Bot (2) chama TRUCO, Humano (1) aumenta (RETRUCO), Bot (2) aceita.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    mocker.patch('builtins.input', return_value='aumentar')
    mock_j2.avaliarJogada.return_value = {"jogada": "quero"}
    
    resultado = partida.escalonamento(
        etapa=0, quem_chamou=2, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="truco"
    )

    assert resultado == {"jogada": "retruco", "resultado": "quero"}
    assert mock_jogo.pontos_mao == 3
    
    captured = capsys.readouterr()
    assert "Você pediu retruco!" in captured.out
    assert "Bot aceitou o retruco!" in captured.out

def test_escalonamento_truco_bot_chama_humano_aumenta_bot_recusa(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Bot (2) chama TRUCO, Humano (1) aumenta (RETRUCO), Bot (2) recusa.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    mocker.patch('builtins.input', return_value='aumentar')
    mock_j2.avaliarJogada.return_value = {"jogada": "não quero"}

    resultado = partida.escalonamento(
        etapa=0, quem_chamou=2, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="truco"
    )

    assert resultado == {
        "jogada": "retruco", 
        "resultado": "não quero", 
        "quem_negou": 2, 
        "pontos": 2
    }

def test_escalonamento_truco_humano_chama_bot_aceita(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Humano (1) chama TRUCO, Bot (2) aceita.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    
    mock_j2.avaliarJogada.side_effect = [
        {"jogada": "quero"},
        {"jogada": "jogar carta"}
    ]
    
    resultado = partida.escalonamento(
        etapa=0, quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="truco"
    )

    assert resultado == {"jogada": "truco", "resultado": "quero"}
    assert mock_jogo.pontos_mao == 2
    
    captured = capsys.readouterr()
    assert "Humano chamou truco!" in captured.out
    assert "Bot aceitou o truco!" in captured.out

def test_escalonamento_truco_humano_chama_bot_aumenta_humano_recusa(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Humano (1) chama TRUCO, Bot (2) aumenta (RETRUCO), Humano (1) recusa.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    
    mock_j2.avaliarJogada.return_value = {"jogada": "retruco"}

    mocker.patch('builtins.input', return_value='n')

    resultado = partida.escalonamento(
        etapa=0, quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="truco"
    )

    assert resultado == {
        "jogada": "retruco", 
        "resultado": "não quero", 
        "quem_negou": 1, 
        "pontos": 2
    }
    captured = capsys.readouterr()
    assert "Bot pediu retruco!" in captured.out
    assert "Humano não quis." in captured.out


def test_escalonamento_envido_humano_chama_bot_recusa(mocks_escalonamento, mocker, capsys):
    """
    Testa Cenário: Humano (1) chama ENVIDO, Bot (2) recusa.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_escalonamento
    
    mock_j2.avaliarJogada.side_effect = [
        {"jogada": "não quero"},
        {"jogada": "jogar carta"} 
    ]
    
    resultado = partida.escalonamento(
        etapa=0, quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, 
        jogo=mock_jogo, escalonamento_tipo="envido"
    )

    assert resultado == {
        "jogada": "envido", 
        "resultado": "não quero", 
        "quem_negou": 2, 
        "pontos": 1
    }
    assert mock_jogo.pontos_mao == 1
    
    captured = capsys.readouterr()
    assert "Bot não quis envido." in captured.out

@pytest.fixture
def mocks_flor(mocker):
    """Fixture que cria mocks de Jogo, Jogador 1 (Humano) e Jogador 2 (Bot)."""
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.rodada_atual = 1
    mock_jogo.pontos_j1 = 0
    mock_jogo.pontos_j2 = 0
    mock_jogo.pontos_maximos = 12
    
    mock_j1 = mocker.MagicMock(nome="Humano")
    mock_j2 = mocker.MagicMock(nome="Bot")    

    mocker.patch('updated_main.atualizar_conhecimento_jogada_especial')

    mocker.patch('updated_main.distribuir_pontos') 

    return mock_jogo, mock_j1, mock_j2


def test_escalonamento_flor_j1_chama_j2_nao_tem(mocks_flor, mocker):
    """
    Testa Cenário: J1 (Humano) canta FLOR, J2 (Bot) não tem flor.
    J1 deve ganhar 3 pontos.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = True
    mock_j2.checaFlor.return_value = False
    
    partida.escalonamento_flor(quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)

    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 1, 3, False)

def test_escalonamento_flor_j2_chama_j1_nao_tem(mocks_flor, mocker):
    """
    Testa Cenário: J2 (Bot) canta FLOR, J1 (Humano) não tem flor.
    J2 deve ganhar 3 pontos.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = False
    mock_j2.checaFlor.return_value = True
    
    partida.escalonamento_flor(quem_chamou=2, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)

    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 2, 3, False)

def test_escalonamento_flor_j1_chama_j2_tem_e_recusa(mocks_flor, mocker):
    """
    Testa Cenário: J1 (Humano) canta FLOR, J2 (Bot) tem flor mas recusa (não quer 'Contra-Flor').
    J1 deve ganhar 3 pontos.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = True
    mock_j2.checaFlor.return_value = True
    
    mock_j2.avaliarJogada.return_value = {"jogada": "não quero"}
    
    partida.escalonamento_flor(quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)

    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 1, 6, False)

def test_escalonamento_flor_j1_chama_j2_aumenta_j1_aceita(mocks_flor, mocker):
    """
    Testa Cenário: J1 canta FLOR, J2 canta CONTRA-FLOR, J1 aceita.
    J2 tem a flor mais alta e ganha 6 pontos.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = True
    mock_j2.checaFlor.return_value = True

    mock_j1.retornarPontosEnvido.return_value = 30
    mock_j2.retornarPontosEnvido.return_value = 33
    
    mock_j2.avaliarJogada.return_value = {"jogada": "contra flor"}

    mocker.patch('builtins.input', return_value='s')
    
    partida.escalonamento_flor(quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)
    
    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 1, 6, False)


def test_escalonamento_flor_j1_chama_j2_aumenta_j1_recusa(mocks_flor, mocker):
    """
    Testa Cenário: J1 canta FLOR, J2 canta CONTRA-FLOR, J1 recusa.
    J2 ganha 4 pontos (pontos_negados[1]).
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = True
    mock_j2.checaFlor.return_value = True
    
    mock_j2.avaliarJogada.return_value = {"jogada": "contra flor"}

    mocker.patch('builtins.input', return_value='n')
    
    partida.escalonamento_flor(quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)
    
    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 1, 4, False)

def test_escalonamento_flor_j1_chama_j1_mente(mocks_flor, mocker, capsys):
    """
    Testa Cenário: J1 canta FLOR, mas não tem flor (mentiu).
    A função deve retornar 'None' imediatamente.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_flor
    
    mock_j1.checaFlor.return_value = False

    resultado = partida.escalonamento_flor(quem_chamou=1, jogador1=mock_j1, jogador2=mock_j2, jogo=mock_jogo)
    captured = capsys.readouterr()

    assert resultado is None
    assert "Jogada inválida!" in captured.out

    partida.distribuir_pontos.assert_not_called()

@pytest.fixture
def mocks_realizar_jogada(mocker):
    """Fixture que cria mocks para 'realizar_jogada'."""
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.rodada_atual = 1
    
    mock_j1 = mocker.MagicMock(nome="Humano")
    mock_j2 = mocker.MagicMock(nome="Bot")

    mocker.patch('updated_main.escalonamento')
    mocker.patch('updated_main.distribuir_pontos')
    mocker.patch('updated_main.inverter_jogador', return_value=1)
    mocker.patch('updated_main.confrontarEnvido')
    
    return mock_jogo, mock_j1, mock_j2

def test_realizar_jogada_bot_joga_carta(mocks_realizar_jogada, mocker):
    """
    Testa o caminho mais simples do Bot:
    Ele avalia e decide 'jogar carta' imediatamente.
    """
    mock_jogo, mock_j1_adv, mock_j2_bot = mocks_realizar_jogada
    
    mock_carta_jogada = mocker.MagicMock(spec=Carta)
    
    mock_j2_bot.avaliarJogada.return_value = {
        "jogada": "jogar carta",
        "carta": mock_carta_jogada
    }
    
    carta_retornada = partida.realizar_jogada(
        jogador=mock_j2_bot,
        adversario=mock_j1_adv,
        jogo=mock_jogo,
        rodada=1,
        is_bot=True
    )

    assert carta_retornada == mock_carta_jogada
    mock_carta_jogada.printarCarta.assert_called_once()

    partida.escalonamento.assert_not_called()

def test_realizar_jogada_bot_chama_truco_e_humano_recusa(mocks_realizar_jogada, mocker):
    """
    Testa o Bot chamando 'truco', e a mão encerrando.
    """
    mock_jogo, mock_j1_adv, mock_j2_bot = mocks_realizar_jogada

    mock_j2_bot.avaliarJogada.side_effect = [
        {"jogada": "truco"},
        {"jogada": "jogar carta", "carta": "carta_nao_deve_ser_jogada"}
    ]

    partida.escalonamento.return_value = {
        "resultado": "não quero",
        "quem_negou": 1,
        "pontos": 1
    }

    carta_retornada = partida.realizar_jogada(
        jogador=mock_j2_bot,
        adversario=mock_j1_adv,
        jogo=mock_jogo,
        rodada=1,
        is_bot=True
    )

    partida.escalonamento.assert_called_once_with(0, 2, mock_j1_adv, mock_j2_bot, mock_jogo, 'truco')

    partida.inverter_jogador.assert_called_with(1)
    partida.distribuir_pontos.assert_called_once_with(mock_jogo, 1, 1, True)

    assert carta_retornada is None
    
    assert mock_j2_bot.avaliarJogada.call_count == 1

def test_realizar_jogada_humano_joga_carta(mocks_realizar_jogada, mocker):
    """
    Testa o caminho simples do Humano:
    Ele escolhe 'jogar carta' no menu.
    """
    mock_jogo, mock_j1_humano, mock_j2_bot_adv = mocks_realizar_jogada
    
    mocker.patch('updated_main.menu_jogador', return_value=1)
    
    mock_carta_jogada = mocker.MagicMock(spec=Carta)
    mock_carta_jogada.retornarPontosCarta.return_value = 10

    mock_j1_humano.jogarCarta.return_value = mock_carta_jogada

    carta_retornada = partida.realizar_jogada(
        jogador=mock_j1_humano,
        adversario=mock_j2_bot_adv,
        jogo=mock_jogo,
        rodada=1,
        is_bot=False
    )
    
    assert carta_retornada == mock_carta_jogada

    partida.menu_jogador.assert_called_once_with(mock_j1_humano)

    mock_j1_humano.jogarCarta.assert_called_once_with(1)
    mock_j2_bot_adv.atualizarRegistro.assert_called_once_with(
        ["primeiraCartaHumano"],
        [10]
    )
    partida.escalonamento.assert_not_called()

@pytest.fixture
def mocks_processar_rodada(mocker):
    """Fixture que cria mocks para 'processar_rodada'."""
    mock_jogo = mocker.MagicMock(spec=Jogo)
    mock_jogo.rodada_atual = 0
    mock_jogo.quemJogaPrimeiro = 1
    mock_jogo.jogador_mao = 1
    mock_jogo.rodadas_vencedor = [0, 0, 0]
    mock_jogo.encerrar_mao = False
    
    mock_j1 = mocker.MagicMock(nome="Humano")
    mock_j2 = mocker.MagicMock(nome="Bot")
    
    mocker.patch('updated_main.realizar_jogada')
    mocker.patch('updated_main.verificar_ganhador')
    mocker.patch('updated_main.distribuir_pontos')
    return mock_jogo, mock_j1, mock_j2

def test_processar_rodada_j1_joga_primeiro_e_ganha(mocks_processar_rodada, mocker):
    """
    Testa o fluxo de uma rodada onde J1 (Humano) joga primeiro e ganha.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_processar_rodada
    
    mock_carta_j1 = mocker.MagicMock(spec=Carta, name="CartaJ1")
    mock_carta_j2 = mocker.MagicMock(spec=Carta, name="CartaJ2")
    
    partida.realizar_jogada.side_effect = [mock_carta_j1, mock_carta_j2]
    
    mock_jogo.verificarCartaVencedora.return_value = mock_carta_j1
    
    partida.processar_rodada(mock_jogo, mock_j1, mock_j2, rodada_atual=1)
    
    assert mock_jogo.rodada_atual == 1
    
    calls = partida.realizar_jogada.call_args_list
    assert len(calls) == 2

    assert calls[0].args == (mock_j1, mock_j2, mock_jogo, 1, False)

    assert calls[1].args == (mock_j2, mock_j1, mock_jogo, 1, True)

    mock_jogo.verificarCartaVencedora.assert_called_once_with(mock_carta_j1, mock_carta_j2)
    
    assert mock_jogo.rodadas_vencedor[0] == 1
    assert mock_jogo.quemJogaPrimeiro == 1
    mock_j2.atualizarRegistro.assert_called_once_with(["ganhadorPrimeiraRodada"], [1])

    partida.verificar_ganhador.assert_called_once_with(mock_jogo)

def test_processar_rodada_j2_joga_primeiro_e_empata(mocks_processar_rodada, mocker):
    """
    Testa o fluxo onde J2 (Bot) joga primeiro e a rodada empata.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_processar_rodada
    
    mock_jogo.quemJogaPrimeiro = 2

    mock_jogo.jogador_mao = 1

    mock_carta_j1 = mocker.MagicMock(spec=Carta, name="CartaJ1")
    mock_carta_j2 = mocker.MagicMock(spec=Carta, name="CartaJ2")

    partida.realizar_jogada.side_effect = [mock_carta_j2, mock_carta_j1]

    mock_jogo.verificarCartaVencedora.return_value = "Empate"
    
    partida.processar_rodada(mock_jogo, mock_j1, mock_j2, rodada_atual=2)

    calls = partida.realizar_jogada.call_args_list
    assert len(calls) == 2

    assert calls[0].args == (mock_j2, mock_j1, mock_jogo, 2, True)

    assert calls[1].args == (mock_j1, mock_j2, mock_jogo, 2, False)

    mock_jogo.verificarCartaVencedora.assert_called_once_with(mock_carta_j1, mock_carta_j2)

    assert mock_jogo.rodadas_vencedor[1] == 3
    assert mock_jogo.quemJogaPrimeiro == 1
    mock_j2.atualizarRegistro.assert_called_once_with(["ganhadorSegundaRodada"], [0])

def test_processar_rodada_interrompida_por_truco(mocks_processar_rodada):
    """
    Testa o fluxo onde a rodada é interrompida (ex: truco negado).
    'realizar_jogada' deve retornar None.
    """
    mock_jogo, mock_j1, mock_j2 = mocks_processar_rodada

    partida.realizar_jogada.return_value = None

    partida.processar_rodada(mock_jogo, mock_j1, mock_j2, rodada_atual=1)
    
    partida.realizar_jogada.assert_called_once()
    
    mock_jogo.verificarCartaVencedora.assert_not_called()
    
    mock_j2.atualizarRegistro.assert_not_called()

    partida.verificar_ganhador.assert_called_once_with(mock_jogo)

def test_inicializar_jogo(mocker):
    """
    Testa se 'inicializar_jogo' cria e configura todos os objetos corretamente.
    """
    mock_baralho_inst = mocker.MagicMock(spec=Baralho)
    mock_baralho_class = mocker.patch('updated_main.Baralho', return_value=mock_baralho_inst)
    mock_cbr_inst = mocker.MagicMock(spec=Cbr)
    mock_cbr_class = mocker.patch('updated_main.Cbr', return_value=mock_cbr_inst)
    mock_jogo_inst = mocker.MagicMock(spec=Jogo)
    mock_j1 = mocker.MagicMock(spec=Jogador)
    mock_j2 = mocker.MagicMock(spec=Bot)
    mock_jogo_inst.criarJogador.return_value = mock_j1
    mock_jogo_inst.criarBot.return_value = mock_j2
    mock_jogo_class = mocker.patch('updated_main.Jogo', return_value=mock_jogo_inst)
    
    jogo, baralho, jogador1, jogador2 = partida.inicializar_jogo()
    
    mock_baralho_class.assert_called_once()
    mock_cbr_class.assert_called_once()
    mock_jogo_class.assert_called_once()
    
    mock_baralho_inst.criarBaralho.assert_called_once()
    mock_baralho_inst.embaralhar.assert_called_once()
    
    mock_jogo_inst.criarJogador.assert_called_once_with("Luís Alvaro", mock_baralho_inst)
    mock_jogo_inst.criarBot.assert_called_once_with("Bot", mock_baralho_inst, mock_cbr_inst)

    assert jogo == mock_jogo_inst
    assert baralho == mock_baralho_inst
    assert jogador1 == mock_j1
    assert jogador2 == mock_j2


def test_resetar_jogo(mocker):
    """
    Testa se 'resetar_jogo' chama todos os métodos de reset e criação de mão.
    """
    mock_j1 = mocker.MagicMock(spec=Jogador)
    mock_j2 = mocker.MagicMock(spec=Bot)
    mock_baralho = mocker.MagicMock(spec=Baralho)
    mock_jogo = mocker.MagicMock(spec=Jogo)
    
    partida.resetar_jogo(mock_j1, mock_j2, mock_baralho, mock_jogo)
    
    mock_j1.resetar.assert_called_once()
    mock_j2.resetar.assert_called_once()
    mock_baralho.resetarBaralho.assert_called_once()
    mock_jogo.resetarJogo.assert_called_once()
    
    mock_baralho.criarBaralho.assert_called_once()
    mock_baralho.embaralhar.assert_called_once()
    
    mock_j1.criarMao.assert_called_once_with(mock_baralho)
    mock_j2.criarMao.assert_called_once_with(mock_baralho)

def test_menu_jogador_entrada_valida(mocker, capsys):
    """
    Testa 'menu_jogador' com uma entrada válida (opção 2).
    """
    mock_jogador = mocker.MagicMock(spec=Jogador)

    mocker.patch('builtins.input', return_value='2')

    opcao = partida.menu_jogador(mock_jogador)

    assert opcao == 2
    mock_jogador.mostrarMao.assert_called_once()

def test_menu_jogador_entrada_invalida_depois_valida(mocker, capsys):
    """
    Testa 'menu_jogador' com entradas inválidas (texto, número fora do range)
    seguidas por uma válida.
    """
    mock_jogador = mocker.MagicMock(spec=Jogador)
    
    mocker.patch('builtins.input', side_effect=['texto', '15', '1'])
    
    opcao = partida.menu_jogador(mock_jogador)

    assert opcao == 1
    mock_jogador.mostrarMao.assert_called_once()
    
    captured = capsys.readouterr()
    assert "Opção inválida. Tente novamente." in captured.out

    assert builtins.input.call_count == 3

def test_realizar_jogada_humano_chama_truco_prova_loop_infinito(mocks_realizar_jogada, mocker):
    """
    Este teste simula o humano fazendo duas ações:
    1. Chamando 'Truco' (opção 4)
    2. Jogando uma carta (opção 1)
    """
    mock_jogo, mock_j1_humano, mock_j2_bot_adv = mocks_realizar_jogada
    
    mocker.patch('updated_main.menu_jogador', side_effect=[4, 1])

    partida.escalonamento.return_value = {"resultado": "quero"}

    mock_carta_jogada = mocker.MagicMock(spec=Carta)
    mock_j1_humano.jogarCarta.return_value = mock_carta_jogada
    mock_carta_jogada.retornarPontosCarta.return_value = 10
    
    carta_retornada = partida.realizar_jogada(
        jogador=mock_j1_humano,
        adversario=mock_j2_bot_adv,
        jogo=mock_jogo,
        rodada=1,
        is_bot=False
    )
    
    assert partida.menu_jogador.call_count == 2

    partida.escalonamento.assert_called_once()
    mock_j1_humano.jogarCarta.assert_called_once_with(1)
    
    assert carta_retornada == mock_carta_jogada