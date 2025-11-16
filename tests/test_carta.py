import pytest

from carta import Carta
from pontos import MANILHA, CARTAS_VALORES

# --- PASSO 1: Injetar Dependências ---
@pytest.fixture
def dummy_carta():
    """ 
    Instância "dummy" da classe Carta.
    """
    return Carta(None, None)

# --- PASSO 2: Testes ---
def test_verificar_carta_alta_duas_manilhas(dummy_carta):
    """
    Testa verificarCartaAlta com duas manilhas.
    """
    carta_01 = Carta(1, "ESPADAS")
    carta_02 = Carta(1, "BASTOS")    

    resultado = dummy_carta.verificarCartaAlta(carta_01, carta_02)
    assert resultado == carta_01

def test_verificar_carta_alta_uma_manilha(dummy_carta):
    """
    Testa verificarCartaAlta com uma manilha.
    """
    carta_01 = Carta(1, "ESPADAS")
    carta_02 = Carta(3, "OUROS")    

    resultado = dummy_carta.verificarCartaAlta(carta_01, carta_02)
    assert resultado == carta_01

def testar_verificar_carta_alta_sem_manilhas(dummy_carta):
    """
    Testa verificarCartaAlta sem manilhas.
    """
    carta_01 = Carta(3, "OUROS")
    carta_02 = Carta(2, "COPAS")    

    resultado = dummy_carta.verificarCartaAlta(carta_01, carta_02)
    assert resultado == carta_01

def test_verificar_carta_alta_igualdade(dummy_carta):
    """
    Testa verificarCartaAlta com cartas iguais.
    """
    carta_01 = Carta(3, "OUROS")
    carta_02 = Carta(3, "OUROS")    

    resultado = dummy_carta.verificarCartaAlta(carta_01, carta_02)
    assert resultado == carta_01

def test_verificar_carta_baixa_duas_manilhas(dummy_carta):
    """
    Testa verificarCartaBaixa com duas manilhas.
    """
    carta_01 = Carta(1, "BASTOS")
    carta_02 = Carta(1, "ESPADAS")    

    resultado = dummy_carta.verificarCartaBaixa(carta_01, carta_02)
    assert resultado == carta_01

def test_verificar_carta_baixa_uma_manilha(dummy_carta):
    """
    Testa verificarCartaBaixa com uma manilha.
    """
    carta_01 = Carta(3, "OUROS")
    carta_02 = Carta(1, "ESPADAS")    

    resultado = dummy_carta.verificarCartaBaixa(carta_01, carta_02)
    assert resultado == carta_01

def testar_verificar_carta_baixa_sem_manilhas(dummy_carta):
    """
    Testa verificarCartaBaixa sem manilhas.
    """
    carta_01 = Carta(2, "COPAS")
    carta_02 = Carta(3, "OUROS")    

    resultado = dummy_carta.verificarCartaBaixa(carta_01, carta_02)
    assert resultado == carta_01

def test_verificar_carta_baixa_igualdade(dummy_carta):
    """
    Testa verificarCartaBaixa com cartas iguais.
    """
    carta_01 = Carta(3, "OUROS")
    carta_02 = Carta(3, "OUROS")    

    resultado = dummy_carta.verificarCartaBaixa(carta_01, carta_02)
    assert resultado == carta_01

def test_carta_manilha_true(dummy_carta):
    """
    Testa cartaManilha retornando True.
    """
    espadao = Carta(1, "ESPADAS")
    bastiao = Carta(1, "BASTOS")
    manilha = Carta(7, "ESPADAS")
    maneca = Carta(7, "OUROS")

    cartas_dummy = [espadao, bastiao, manilha, maneca]
    
    for carta in cartas_dummy:
        assert dummy_carta.cartaManilha(carta) == True

def test_carta_manilha_false(dummy_carta):
    """
    Testa cartaManilha retornando False.
    """
    carta = Carta(3, "OUROS")
    assert dummy_carta.cartaManilha(carta) == False

def test_retornar_pontos_carta_manilha(dummy_carta):
    """
    Testa retornarPontosCarta para manilhas.
    """
    espadao = Carta(1, "ESPADAS")
    bastiao = Carta(1, "BASTOS")
    manilha_espadas = Carta(7, "ESPADAS")
    manilha_ouros = Carta(7, "OUROS")

    assert dummy_carta.retornarPontosCarta(espadao) == 52
    assert dummy_carta.retornarPontosCarta(bastiao) == 50
    assert dummy_carta.retornarPontosCarta(manilha_espadas) == 42
    assert dummy_carta.retornarPontosCarta(manilha_ouros) == 40

def test_retornar_pontos_carta_comum(dummy_carta):
    """
    Testa retornarPontosCarta para cartas comuns.
    """
    carta_3 = Carta(3, "OUROS")
    carta_2 = Carta(2, "COPAS")
    carta_1 = Carta(1, "OUROS")
    carta_12 = Carta(12, "ESPADAS")
    carta_11 = Carta(11, "OUROS")
    carta_10 = Carta(10, "COPAS")
    carta_7 = Carta(7, "BASTOS")
    carta_6 = Carta(6, "ESPADAS")
    carta_5 = Carta(5, "OUROS")
    carta_4 = Carta(4, "COPAS")

    assert dummy_carta.retornarPontosCarta(carta_3) == 24
    assert dummy_carta.retornarPontosCarta(carta_2) == 16
    assert dummy_carta.retornarPontosCarta(carta_1) == 12
    assert dummy_carta.retornarPontosCarta(carta_12) == 8
    assert dummy_carta.retornarPontosCarta(carta_11) == 7
    assert dummy_carta.retornarPontosCarta(carta_10) == 6
    assert dummy_carta.retornarPontosCarta(carta_7) == 4
    assert dummy_carta.retornarPontosCarta(carta_6) == 3
    assert dummy_carta.retornarPontosCarta(carta_5) == 2
    assert dummy_carta.retornarPontosCarta(carta_4) == 1

def test_classificar_carta(dummy_carta):
    """
    Testa classificarCarta com várias combinações.
    """
    carta_01 = Carta(1, "ESPADAS")
    carta_02 = Carta(3, "OUROS")
    carta_03 = Carta(2, "COPAS")
    cartas = [carta_01, carta_02, carta_03]
    pontos, classificacao = dummy_carta.classificarCarta(cartas)

    assert classificacao[0] == "Alta"
    assert pontos[0] == 52

    assert classificacao[1] == "Media"
    assert pontos[1] == 24

    assert classificacao[2] == "Baixa"
    assert pontos[2] == 16

    cartas_2 = [carta_02, carta_03, carta_01]
    pontos_2, classificacao_2 = dummy_carta.classificarCarta(cartas_2)
    assert classificacao_2 == ['Media', 'Baixa', 'Alta']
    assert pontos_2 == [24, 16, 52]

def test_printar_carta_manilha(capsys):
    """
    Testa a saída de printarCarta.
    """
    carta = Carta(1, "ESPADAS")
    carta.printarCarta(i=None)

    captured = capsys.readouterr()
    saida = captured.out

    assert saida == "[X] ESPADÃO +\n"

def test_printar_carta_comum(capsys):
    """
    Testa a saída de printarCarta para carta comum.
    """
    carta = Carta(3, "OUROS")
    carta.printarCarta(i=1)

    captured = capsys.readouterr()
    saida = captured.out

    assert saida == "[1] 3 de OUROS\n"

def test_retornar_numero_carta_manilha():
    """
    Testa se o número da carta manilha é retornado corretamente.
    """
    carta = Carta(1, "ESPADAS")
    assert carta.retornarNumero() == 1

def test_retornar_numero_carta_comum():
    """
    Testa se o número da carta comum é retornado corretamente.
    """
    carta = Carta(5, "COPAS")
    assert carta.retornarNumero() == 5

def test_retornar_naipe_carta_manilha():
    """
    Testa se o naipe da carta manilha é retornado corretamente.
    """
    carta = Carta(1, "BASTOS")
    assert carta.naipe == "BASTOS"

def test_retornar_naipe_carta_comum():
    """
    Testa se o naipe da carta comum é retornado corretamente.
    """
    carta = Carta(5, "COPAS")
    assert carta.naipe == "COPAS"