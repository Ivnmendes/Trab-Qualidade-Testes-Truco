import pytest
import random

import baralho as baralho_module
from baralho import Baralho
import carta as carta_module

# --- PASSO 1: Injetar Dependências ---
# Esta fixture será executada antes de CADA teste
# para garantir que todas as dependências estejam no lugar.

@pytest.fixture(autouse=True)
def patch_dependencias(monkeypatch):
    """
    Esta fixture faz duas coisas essenciais:
    1. Engana 'carta.py': Fornece dicionários falsos para 'MANILHA' e 
       'CARTAS_VALORES', que são importados de 'pontos.py'.
    2. Engana 'baralho.py': Injeta a classe 'Carta' REAL (que acabamos 
       de importar) em 'baralho.py'.
    """
    
    # 1. Mock das dependências do módulo 'carta' (pontos.py)
    monkeypatch.setattr(carta_module, 'MANILHA', {})
    monkeypatch.setattr(carta_module, 'CARTAS_VALORES', {})

    # 2. Injetando a classe 'Carta' real no módulo 'baralho'
    monkeypatch.setattr(baralho_module, 'Carta', carta_module.Carta)


# --- PASSO 2: Testes ---

def test_init_e_criar_baralho():
    """
    Testa se o baralho é criado corretamente.
    Agora, b.cartas conterá objetos 'Carta' REAIS.
    """
    b = Baralho()

    assert b.manilhas == []
    
    # Verifica se as cartas foram criadas
    assert b.cartas is not None
    assert len(b.cartas) == 40
    
    # Verifica se o primeiro e o último objeto são instâncias reais de Carta
    assert isinstance(b.cartas[0], carta_module.Carta)
    assert isinstance(b.cartas[-1], carta_module.Carta)

def test_conteudo_do_baralho():
    """
    Verifica se as cartas corretas (e incorretas) estão no baralho.
    Procuramos pelos atributos.
    """
    b = Baralho()
    
    # Procura por uma carta que DEVE existir
    achou_as_de_espadas = any(
        c.numero == 1 and c.naipe == "ESPADAS" for c in b.cartas
    )
    assert achou_as_de_espadas, "Não encontrou o Ás de Espadas"
    
    achou_rei_de_copas = any(
        c.numero == 12 and c.naipe == "COPAS" for c in b.cartas
    )
    assert achou_rei_de_copas, "Não encontrou o Rei de Copas"

    # Procura por uma carta que NÃO DEVE existir
    achou_oito_de_bastos = any(
        c.numero == 8 and c.naipe == "BASTOS" for c in b.cartas
    )
    assert not achou_oito_de_bastos, "Encontrou um 8 de Bastos (inválido)"
    
    achou_nove_de_espadas = any(
        c.numero == 9 and c.naipe == "ESPADAS" for c in b.cartas
    )
    assert not achou_nove_de_espadas, "Encontrou um 9 de Espadas (inválido)"

def test_embaralhar_deterministico(monkeypatch):
    """
    Testa o embaralhamento de forma previsível.
    Este teste funciona quase igual, mas agora 'b.cartas' é uma lista
    de objetos 'Carta' reais.
    """
    b = Baralho()
    cartas_ordenadas = list(b.cartas)
    
    # Função falsa que apenas inverte a lista
    def mock_shuffle_inverter(lista):
        lista.reverse()
        
    monkeypatch.setattr(random, 'shuffle', mock_shuffle_inverter)
    
    b.embaralhar()
    
    # Cria a lista esperada (objetos invertidos)
    cartas_esperadas = list(cartas_ordenadas)
    cartas_esperadas.reverse()
    
    # A comparação de listas com '==' funciona, pois ela compara
    # se os mesmos objetos estão na mesma ordem.
    assert b.cartas == cartas_esperadas
    assert b.cartas != cartas_ordenadas

def test_retirar_carta():
    """
    Testa se retirarCarta remove e retorna a última carta.
    Compara por atributos.
    """
    b = Baralho()
    tamanho_original = len(b.cartas)
    
    # A última carta do baralho recém-criado é 12 de BASTOS
    carta_retirada = b.retirarCarta()
    
    # Verifica se a carta correta foi retornada
    assert carta_retirada.numero == 12
    assert carta_retirada.naipe == "BASTOS"
    
    # Verifica se o tamanho do baralho diminuiu
    assert len(b.cartas) == tamanho_original - 1
    
    # Verifica se a carta foi realmente removida da lista
    achou_carta_retirada = any(
        c.numero == 12 and c.naipe == "BASTOS" for c in b.cartas
    )
    assert not achou_carta_retirada

def test_resetar_baralho():
    """Testa se o baralho é limpo corretamente."""
    b = Baralho()
    
    # Modificamos o estado usando a Carta real
    b.retirarCarta()
    b.manilhas = [carta_module.Carta(1, "OUROS")]
    b.vira = [carta_module.Carta(2, "COPAS")] 
    
    # Verificamos que não está no estado inicial
    assert len(b.cartas) != 40
    assert b.manilhas != []
    assert b.vira != []
    
    b.resetarBaralho()
    
    # Verificamos se tudo foi limpo
    assert b.cartas == []
    assert b.manilhas == []
    assert b.vira == []

def test_printar_baralho(capsys):
    """
    Testa se o output de printarBaralho usa a função 'printarCarta' real corretamente.
    """
    b = Baralho()
    # Usamos Cartas reais com saídas especiais
    b.cartas = [
        carta_module.Carta(1, "ESPADAS"), # ESPADÃO
        carta_module.Carta(7, "COPAS")     # Carta comum
    ]
    
    b.printarBaralho()
    
    captured = capsys.readouterr()
    saida = captured.out
    
    # O 'i=None' em printarBaralho -> printarCarta faz com que 'i' vire "X"
    assert "[X] ESPADÃO +\n" in saida
    assert "[X] 7 de COPAS\n" in saida
    assert "[X] 12 de BASTOS" not in saida

def test_printar_manilhas(capsys):
    """Testa a saída de printarManilhas com Cartas reais."""
    b = Baralho()
    b.manilhas = [
        carta_module.Carta(10, "OUROS"),    # Comum
        carta_module.Carta(1, "BASTOS")    # BASTIÃO
    ]
    
    b.printarManilhas()
    captured = capsys.readouterr()
    saida = captured.out
    
    assert "[X] 10 de OUROS\n" in saida
    assert "[X] BASTIÃO +\n" in saida

def test_printar_vira(capsys):
    """Testa a saída de printarVira com uma Carta real."""
    b = Baralho()
    b.vira = [carta_module.Carta(7, "OUROS")] # Sete de Ouros
    
    b.printarVira()
    captured = capsys.readouterr()
    saida = captured.out
    
    assert "[X] Sete de Ouros +\n" in saida