import pandas as pd
import os
from collections import Counter
from pontos import ENVIDO

path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modelo_registro.csv")

class Bot():

    def __init__(self, nome, cbr):
        self.nome = nome
        self.mao = []
        self.maoRank = []
        self.indices = []
        self.pontuacaoCartas = []
        self.forcaMao = 0
        self.pontos = 0
        self.rodadas = 0
        self.envido = 0
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediuTruco = False
        self.ja_respondeu = {
            'truco': False,
            'retruco': False,
            'vale_quatro': False,
            'envido': False,
            'real envido': False,
            'falta envido': False,
            'contra flor': False,
            'contra flor e resto': False
        }
        self.modeloRegistro = pd.read_csv(path, index_col='idMao')
        self.cbr = cbr

    def criarMao(self, baralho):
        self.indices = [0, 1, 2]
        
        # Mudar forma de classificação dos dados vindos da base de casos, para ter uma métrica extra de inserção
        for i in range(3):
            self.mao.append(baralho.retirarCarta())
        self.flor = self.checaFlor()

        if self.flor:
            self.atualizarRegistro(['pontosFlorRobo'], [retornarPontosEnvido(self.mao)])

        self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        self.forcaMao = sum(self.pontuacaoCartas)
        self.inicializarRegistro()
    
    def jogarCarta(self):
        registro_dict = self.modeloRegistro.reset_index().iloc[0].to_dict()
        similiares = self.cbr.buscarSimilares(registro_dict)
        df = pd.DataFrame(similiares)

        if df.empty:
            carta_escolhida = min(self.pontuacaoCartas)
        else:
            carta_escolhida = 0
            ordem = (
                "primeira" if len(self.indices) == 3 else
                "segunda"  if len(self.indices) == 2 else
                "terceira"
            )
            col = ordem + "CartaRobo"

            for aux in reversed(df[col].value_counts().index):
                if aux in self.pontuacaoCartas:
                    carta_escolhida = aux
                    break

            if(carta_escolhida == 0):
                valor_referencia = df[col].value_counts().idxmax()
                carta_escolhida = min(self.pontuacaoCartas, key=lambda x:abs(x-valor_referencia))

        indice = self.pontuacaoCartas.index(carta_escolhida)
        self.indices.remove(indice)
        self.pontuacaoCartas.pop(indice)
        self.indices = self.AjustaIndicesMao(len(self.indices))
        return self.mao.pop(indice)


    def AjustaIndicesMao(self, tam_mao):
        if(tam_mao) == 2:
            return [0, 1]
        
        if(tam_mao) == 1:
            return [0]

    def mostrarMao(self):
        i = 0
        for carta in self.mao:
            carta.printarCarta(i)
            i += 1
    
    def resetar(self):
        self.mao = []
        self.flor = False
        self.ja_respondeu = {
            'truco': False,
            'retruco': False,
            'vale_quatro': False,
            'envido': False,
            'real envido': False,
            'falta envido': False,
            'contra flor': False,
            'contra flor e resto': False
        }
    
    def checaFlor(self):
        if all(carta.retornarNaipe() == self.mao[0].retornarNaipe() for carta in self.mao):
            self.flor = True
            return True
        return False
    
    def inicializarRegistro(self):
        self.modeloRegistro = pd.read_csv(path, index_col='idMao')
        self.modeloRegistro.cartaAltaRobo = self.pontuacaoCartas[self.maoRank.index("Alta")]
        self.modeloRegistro.cartaMediaRobo = self.pontuacaoCartas[self.maoRank.index("Media")]
        self.modeloRegistro.cartaBaixaRobo = self.pontuacaoCartas[self.maoRank.index("Baixa")]
        self.modeloRegistro.pontosEnvidoRobo = retornarPontosEnvido(self.mao)
        self.modeloRegistro.ganhadorPrimeiraRodada = 2
        self.modeloRegistro.ganhadorSegundaRodada = 2
        self.modeloRegistro.ganhadorTerceiraRodada = 2

    def _obterRegistroUtil(self):
        # Retorna todas as colunas do modeloRegistro com valores diferentes de 0
        registro = {col: val for col, val in self.modeloRegistro.iloc[0].items() if val != 0}
        return registro

    def _decisaoMajoritariaPorRodada(self, decisao_col: str, quando_col, rodada: int, valor_aceito) -> bool:
        registro = self._obterRegistroUtil()
        if quando_col is not None:
            if quando_col in registro and registro[quando_col] != rodada:
                registro.pop(quando_col)
        casos_similares = self.cbr.buscarSimilares(registro)

        if not casos_similares:
            # print("Sem casos similares encontrados")
            return False

        if quando_col is not None:
            casos_filtrados = [case for case in casos_similares if case.get(quando_col, 0) == rodada]
        else:
            casos_filtrados = casos_similares

        if not casos_filtrados:
            return False
        decisions = [case.get(decisao_col) for case in casos_filtrados]
        counter = Counter(decisions)

        # print(f"Jogadas consideradas para '{decisao_col}' na rodada {rodada}: {decisions}")
        # print("Jogada retornada:\n")
        # print(counter.get(valor_aceito, 0) > (sum(counter.values()) / 2))
        return counter.get(valor_aceito, 0) > (sum(counter.values()) / 2)
    
    def avaliarContraFlor(self, rodada):
        return self._decisaoMajoritariaPorRodada("quemContraFlor", None, rodada, 2)
    
    def avaliarContraFlorResto(self, rodada):
        return self._decisaoMajoritariaPorRodada("quemContraFlorResto", None, rodada, 2)

    def avaliarTruco(self, rodada):
        return self._decisaoMajoritariaPorRodada("quemTruco", "quandoTruco", rodada, 2)
    
    def avaliarAceitarTruco(self, rodada):
        return not self._decisaoMajoritariaPorRodada("quemNegouTruco", None, rodada, 2)

    def avaliarRetruco(self, rodada):
        if self.modeloRegistro.iloc[0]["quemTruco"] == 1:
            return self._decisaoMajoritariaPorRodada("quemRetruco", "quandoRetruco", rodada, 2)
        else: 
            return False

    def avaliarValeQuatro(self, rodada):
        return self._decisaoMajoritariaPorRodada("quemValeQuatro", "quandoValeQuatro", rodada, 2)

    def avaliarEnvido(self, rodada):
        if (self.modeloRegistro.iloc[0]["quemTruco"] == 2) or (self.modeloRegistro.iloc[0]["quemPediuEnvido"] != 0):
            return False
        return self._decisaoMajoritariaPorRodada("quemPediuEnvido", None, rodada, 2)
    
    def avaliarAceitarEnvido(self, rodada):
        if (self.modeloRegistro.iloc[0]["quemPediuEnvido"] == 0):
            return False
        return not self._decisaoMajoritariaPorRodada("quemNegouEnvido", None, rodada, 2)

    def avaliarRealEnvido(self, rodada):
        if (self.modeloRegistro.iloc[0]["quemTruco"] == 2) or (self.modeloRegistro.iloc[0]["quemPediuEnvido"] == 2) or (self.modeloRegistro.iloc[0]["quemPediuRealEnvido"] != 0):
            return False
        return self._decisaoMajoritariaPorRodada("quemPediuRealEnvido", None, rodada, 2)
    
    def avaliarFaltaEnvido(self, rodada):
        if (self.modeloRegistro.iloc[0]["quemTruco"] == 2) or (self.modeloRegistro.iloc[0]["quemPediuRealEnvido"] == 2) or (self.modeloRegistro.iloc[0]["quemPediuFaltaEnvido"] != 0):
            return False
        return self._decisaoMajoritariaPorRodada("quemPediuFaltaEnvido", None, rodada, 2)
    
    def avaliarJogada(self, rodada: int):
        registro = self._obterRegistroUtil()
        # print("Bot avaliando jogada")
        print("Registro:", registro)
        # for carta in self.mao:
        #     carta.printarCarta()
        # Bot vai considerar primeiro as respostas a serem dadas e se nenhuma condição for verdadeira propõe uma jogada
        # Vai requerer portanto 2 respostas do bot, uma dizendo que aceita a jogada e outra a resposta
        # Ordem de resposta: contra-flor, falta envido, real envido, envido, vale quatro, retruco, truco e uma resposta

        #print("Bot avaliando se precisa dar resposta")
        if rodada == 1:
            #print("Bot avaliando contra flor e resto")
            if self.flor == True:
                if registro.get('quemContraFlor') == 1:
                        if not self.ja_respondeu('contra flor e resto'):
                            aceitar = self.avaliarContraFlorResto(rodada)
                            self.ja_respondeu['contra flor resto'] = True
                            if aceitar:
                                return {'jogada': 'contra flor resto'}
                            aceitar = self.avaliarContraFlor(rodada)
                            return {'jogada': 'quero' if aceitar else 'não quero'}

            #print("Bot avaliando resposta contra flor")
            if self.flor == True:
                if registro.get('quemFlor') == 1:
                        if not self.ja_respondeu('contra flor'):
                            aceitar = self.avaliarContraFlor(rodada)
                            self.ja_respondeu['contra flor'] = True
                            return {'jogada': 'contra flor' if aceitar else 'não quero'}

            #print("Bot avaliando resposta envido")
            if registro.get('quemPediuEnvido') == 1:
                if not self.ja_respondeu['envido']:
                    aceitar = self.avaliarAceitarEnvido(rodada)
                    self.ja_respondeu['envido'] = True
                    return {'jogada': 'quero' if aceitar else 'não quero'}


            #print("Bot avaliando resposta real envido")
            if registro.get('quemPediuRealEnvido') == 1:
                if not self.ja_respondeu['real envido']:
                    aceitar = self.avaliarAceitarEnvido(rodada)
                    self.ja_respondeu['real envido'] = True
                    return {'jogada': 'quero' if aceitar else 'não quero'}
                
            #print("Bot avaliando resposta falta envido")
            if registro.get('quemPediuFaltaEnvido') == 1:
                if not self.ja_respondeu['falta envido']:
                    aceitar = self.avaliarAceitarEnvido(rodada)
                    self.ja_respondeu['falta envido'] = True
                    return {'jogada': 'quero' if aceitar else 'não quero'}
            
        #print("Bot verificando resposta truco")
        if registro.get('quemTruco') == 1 and registro.get('quandoTruco') == rodada:
            if not self.ja_respondeu['truco']:
                aceitar = self.avaliarAceitarTruco(rodada)
                self.ja_respondeu['truco'] = True
                return {'jogada': 'quero' if aceitar else 'não quero'}
  

        #print("Bot verificando resposta retruco")
        if registro.get('quemRetruco') == 1 and registro.get('quandoRetruco') == rodada:
            if not self.ja_respondeu['retruco']:
                aceitar = self.avaliarRetruco(rodada)
                self.ja_respondeu['retruco'] = True
                return {'jogada':'quero' if aceitar else 'não quero'}

        #print("Bot verificando resposta vale quatro")
        if registro.get('quemValeQuatro') == 1 and registro.get('quandoValeQuatro') == rodada:
            if not self.ja_respondeu['vale_quatro']:
                aceitar = self.avaliarValeQuatro(rodada)
                self.ja_respondeu['vale_quatro'] = True
                return {'jogada':'quero' if aceitar else 'não quero'}


        #print("Bot avaliando jogada")
        if rodada == 1:
            #print("Bot avaliando flor")
            if registro.get('quemFlor') is None and self.flor == True:
                return {'jogada': 'flor'}
            
            #print("Bot avaliando envido")
            if registro.get('quemPediuEnvido') is None:
                    aceitar = self.avaliarEnvido(rodada)
                    if aceitar:
                        return {'jogada': 'envido'}
            
            #print("Bot avaliando real envido")
            if registro.get('quemPediuRealEnvido') is None:
                    aceitar = self.avaliarRealEnvido(rodada)
                    if aceitar:
                        return {'jogada': 'real envido'}
            #print("Bot avaliando falta envido")
            if registro.get('quemPediuFaltaEnvido') is None:
                    aceitar = self.avaliarFaltaEnvido(rodada)
                    if aceitar:
                        return {'jogada': 'falta envido'}

        #print("Bot avaliando truco")
        if registro.get('quemTruco') is None and registro.get('quandoTruco') is None:
                aceitar = self.avaliarTruco(rodada)
                if aceitar:
                    return {'jogada': 'truco'}
  
        #print("Bot avaliando retruco")
        if registro.get('quemRetruco') is None and registro.get('quandoRetruco') is None and registro.get('quemTruco') == 1:
                aceitar = self.avaliarRetruco(rodada)
                if aceitar:
                    return {'jogada':'retruco'}

        #print("Bot avaliando vale quatro")
        if registro.get('quemValeQuatro') is None and registro.get('quandoValeQuatro') is None and registro.get('quemRetruco') == 1:
                aceitar = self.avaliarValeQuatro(rodada)
                if aceitar:
                    return {'jogada':'vale quatro'}



        #print("Bot avaliando jogada de carta")
        if rodada == 1:
            coluna_carta = "primeiraCartaRobo"
        elif rodada == 2:
            coluna_carta = "segundaCartaRobo"
        elif rodada == 3:
            coluna_carta = "terceiraCartaRobo"
        else:
            coluna_carta = "primeiraCartaRobo"

        casos_similares = self.cbr.buscarSimilares(registro)
        if not casos_similares:
            return {"jogada": "jogar carta", "carta": min(self.pontuacaoCartas)}
        
        # Para a jogada de carta, agrupe os casos com base na coluna da rodada
        decisions = [case.get(coluna_carta, None) for case in casos_similares if case.get(coluna_carta)]
        if not decisions:
            self.atualizarRegistro([coluna_carta], [min(self.pontuacaoCartas)])
            return {"jogada": "jogar carta", "carta": min(self.pontuacaoCartas)}
        counter = Counter(decisions)
        carta_mais_comum = counter.most_common(1)[0][0]
        if carta_mais_comum not in self.pontuacaoCartas:
            carta_selecionada = min(self.mao, key=lambda carta: abs(carta.retornarPontosCarta(carta) - carta_mais_comum))
        else:
            for carta in self.mao:
                if carta.retornarPontosCarta(carta) == carta_mais_comum:
                    carta_selecionada = carta
                    break
        self.mao.remove(carta_selecionada)
        self.atualizarRegistro([coluna_carta], [carta_selecionada.retornarPontosCarta(carta_selecionada)])
        return {"jogada": "jogar carta", "carta": carta_selecionada}

    def atualizarRegistro(self, cols, valores):
        for col, valor in zip(cols, valores):
            if col in self.modeloRegistro.columns:
                self.modeloRegistro[col] = valor

def retornarPontosEnvido(mao):
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