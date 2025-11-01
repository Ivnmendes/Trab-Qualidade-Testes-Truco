from jogador import Jogador
from bot import Bot
from pontos import ENVIDO

class Jogo():

    def __init__(self):
        self.rodadas = None
        self.pontos_j1 = 0
        self.pontos_j2 = 0
        self.pontos_maximos = 12
        self.pontos_mao = None
        self.jogador_mao = 1
        self.truco = None
        self.retruco = None
        self.vale_quatro = None
        self.envido = None
        self.real_envido = None
        self.falta_envido = None
        self.flor = None
        self.contra_flor = None
        self.contra_flor_resto = None
        self.rodadas_vencedor = None
        self.rodada_atual = None
        self.maosJogadas = None
        self.encerrar_mao = None
        self.encerrar_jogo = None
        self.truco_negado = None
        self.resetarJogo()

    def iniciarJogo(self):
        pass

    def resetarJogo(self):
        # Controle geral do jogo
        # Pontos totais por jogador, rodadas jogadas, jogadas chamadas, etc
        self.pontos_mao = 1
        self.truco_negado = False
        self.quemJogaPrimeiro = self.jogador_mao
        self.truco = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 2}
        self.retruco = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 3}
        self.vale_quatro = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 4}
        self.envido = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 2}
        self.real_envido = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 4}
        self.falta_envido = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': self.pontos_maximos}
        self.flor = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 3}
        self.contra_flor = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': 6}
        self.contra_flor_resto = {'quemPediu': 0, 'quandoPediu': 0, 'quemGanhou': 0, 'aceito': None, 'pontos': self.pontos_maximos}
        self.rodadas_vencedor = [0,0,0] # 1 = J1, 2 = J2, 3 = Empate
        self.rodada_atual = -1
        self.maosJogadas = 0
        self.encerrar_mao = False
        self.encerrar_jogo = False

    def criarJogador(self, nome, baralho):
        jogador = Jogador(nome)
        jogador.criarMao(baralho)
        return jogador
    
    def aceitar_pedido(self, quem: int, rodada: int, aceito: bool):
        """
        Aceita ou recusa o primeiro pedido pendente (truco, retruco, vale_quatro,
        envido, real_envido, falta_envido, flor, contra_flor, contra_flor_resto),
        atribui os pontos e registra quem ganhou.
        """
        # lista nome dos atributos
        attrs = [
            'truco', 'retruco', 'vale_quatro',
            'envido', 'real_envido', 'falta_envido',
            'flor', 'contra_flor', 'contra_flor_resto'
        ]
        for name in attrs:
            rec = getattr(self, name)
            # “pedido” ativo quando alguém pediu (quemPediu != 0) e ainda não respondeu (aceito is None)
            if rec['quemPediu'] != 0 and rec['aceito'] is None:
                rec['aceito'] = aceito
                rec['quandoPediu'] = rodada
                return True

        # se chegar aqui, não havia pedido pendente
        print("Não há pedido pendente para aceitar.")
        return False



    def criarBot(self, nome, baralho, cbr):
        bot = Bot(nome, cbr)
        bot.criarMao(baralho)
        return bot
           
    def trocarJogadorMao(self, jogador1, jogador2):
        if self.maoAtual == 1:
            self.maoAtual = 2
        else:
            self.maoAtual = 1

        if jogador1.primeiro:
            jogador1.primeiro = False
            jogador2.primeiro = True
        else:
            jogador1.primeiro = True
            jogador2.primeiro = False
    

    def verificarCartaVencedora(self, carta_jogador_01, carta_jogador_02):
        if carta_jogador_01.retornarPontosCarta(carta_jogador_01) > carta_jogador_02.retornarPontosCarta(carta_jogador_02):
            return carta_jogador_01
        elif carta_jogador_01.retornarPontosCarta(carta_jogador_01) < carta_jogador_02.retornarPontosCarta(carta_jogador_02):
            return carta_jogador_02
        else: return "Empate"
    
    def retornarPontosEnvido(self, mao):
        grupos = {}
        for carta in mao:
            naipe = carta.retornarNaipe()
            pontos_envido = ENVIDO[str(carta.numero)]
            if naipe not in grupos:
                grupos[naipe] = []
            grupos[naipe].append(pontos_envido)
        
        melhor_pontuacao = 0
        for naipe, pontos in grupos.items():
            if len(pontos) >= 2:
                pontos.sort(reverse=True)
                pontuacao = 20 + pontos[0] + pontos[1]
                melhor_pontuacao = max(melhor_pontuacao, pontuacao)
            else:
                pontuacao = pontos[0]
                melhor_pontuacao = max(melhor_pontuacao, pontuacao)
        return melhor_pontuacao