from baralho import Baralho
from jogo import Jogo
from cbr_updated import Cbr

opcoes_jogada = ['Truco', 'Retruco', 'Vale quatro','Envido','Real Envido','Falta Envido', 'Flor']

def escalonamento(etapa: int, quem_chamou: int, jogador1, jogador2, jogo, escalonamento_tipo):
    pontos_escala = None
    nome_etapas = None
    pontos_negados_escala = None

    if escalonamento_tipo == "truco": 
        pontos_escala = {0: 2, 1: 3, 2: 4}
        nome_etapas = {0: "truco", 1: "retruco", 2: "vale quatro"}
        pontos_negados_escala = {0: 1, 1: 2, 2: 3}

    if escalonamento_tipo == "envido": 
        pontos_escala = {0: 2, 1: 6, 2: jogo.pontos_maximos}
        nome_etapas = {0: "envido", 1: "real envido", 2: "falta envido"}
        pontos_negados_escala = {0: 1, 1: 1, 2: 5}
    
    if quem_chamou == 2:  # Bot chamou
        print(f"Bot chamou {nome_etapas[etapa]}!")
        atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, False)
        resposta = input("Você aceita? (s/n/aumentar): ").strip().lower()
        if resposta == 's':
            if escalonamento_tipo == 'truco':
                jogo.pontos_mao = pontos_escala[etapa]
            return { "jogada": nome_etapas[etapa], "resultado": "quero"}
        elif resposta == 'aumentar' and etapa < 2:
            etapa += 1
            print(f"Você pediu {nome_etapas[etapa]}!")
            atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
            jogada_bot = jogador2.avaliarJogada(jogo.rodada_atual)
            if jogada_bot["jogada"] == "quero":
                if escalonamento_tipo == 'truco':
                    jogo.pontos_mao = pontos_escala[etapa]
                print(f"{jogador2.nome} aceitou o {nome_etapas[etapa]}!")
                return { "jogada": nome_etapas[etapa], "resultado": "quero"}
            else:
                print(f"{jogador2.nome} não quis {nome_etapas[etapa]}!")
                return { "jogada": nome_etapas[etapa], "resultado": "não quero", "quem_negou": 2, "pontos": pontos_negados_escala[etapa] }
        else:
            print(f"{jogador1.nome} não quis {nome_etapas[etapa]}!")
            return { "jogada": nome_etapas[etapa], "resultado": "não quero", "quem_negou": 1, "pontos": pontos_negados_escala[etapa] }

    elif quem_chamou == 1:  # Jogador chamou
        print(f"{jogador1.nome} chamou {nome_etapas[etapa]}!")
        atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
        resposta = jogador2.avaliarJogada(jogo.rodada_atual)
        if resposta['jogada'] == 'quero':
            if escalonamento_tipo == 'truco':
                jogo.pontos_mao = pontos_escala[etapa]
        elif resposta['jogada'] == 'não quero':
            print(f"{jogador2.nome} não quis {nome_etapas[etapa]}.")
            atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, True)
            return { "jogada": nome_etapas[etapa], "resultado": "não quero", "quem_negou": 2, "pontos": pontos_negados_escala[etapa] }
        
        resposta = jogador2.avaliarJogada(jogo.rodada_atual)
        if resposta['jogada'] == nome_etapas[etapa+1] and etapa < 2:
            etapa += 1
            print(f"{jogador2.nome} pediu {nome_etapas[etapa]}!")
            atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, False)
            
            resposta = input("Você aceita? (s/n/aumentar): ").strip().lower()
            if resposta == "s":
                if escalonamento_tipo == 'truco':
                    jogo.pontos_mao = pontos_escala[etapa]
                print(f"{jogador1.nome} aceitou o {nome_etapas[etapa]}!")
                return { "jogada": nome_etapas[etapa], "resultado": "quero"}
            elif resposta == "aumentar" and etapa < 2:
                etapa+=1
                atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
                resposta = jogador2.avaliarJogada(jogo.rodada_atual)
                if resposta['jogada'] == 'não quero':
                    print(f'{jogador2.nome} não quis {nome_etapas[etapa]}')
                    atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, True)
                    return { "jogada": nome_etapas[etapa], "resultado": "não quero", "quem_negou": 2, "pontos": pontos_negados_escala[etapa] }
                elif resposta['jogada'] == 'quero':
                    if escalonamento_tipo == 'truco':
                        jogo.pontos_mao = pontos_escala[etapa]
            else:
                print(f"{jogador1.nome} não quis.")
                atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, True)
                return { "jogada": nome_etapas[etapa], "resultado": "não quero", "quem_negou": 1, "pontos": pontos_negados_escala[etapa] }
        else:
            print(f"{jogador2.nome} aceitou o {nome_etapas[0]}!")
            if escalonamento_tipo == 'truco':
                jogo.pontos_mao = pontos_escala[etapa]
            return { "jogada": nome_etapas[0], "resultado": "quero"}
 
def escalonamento_flor(quem_chamou: int, jogador1, jogador2, jogo):
    etapa = 0
    nome_etapas = {0: "flor", 1: "contra flor", 2: "contra flor resto"}
    pontos_escala = {0: 3, 1: 6, 2: jogo.pontos_maximos - max(jogo.pontos_j1, jogo.pontos_j2)}
    pontos_negados = {0: 0, 1: 4, 2: 6}  # Valor que o outro ganha se a aposta não for aceita

    if jogo.rodada_atual != 1 or (jogador1.checaFlor == False and jogador2.checaFlor == False):
        print("Jogada inválida!")
        return

    if quem_chamou == 1:  # Jogador chamou
        if jogador1.checaFlor() == False:
            print("Jogada inválida!")
            return
        
        print(f"{jogador1.nome} pediu {nome_etapas[etapa]}!")
        atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
        if jogador2.checaFlor() == False:
            distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
            return

        resposta = jogador2.avaliarJogada(jogo.rodada_atual)
        if resposta["jogada"] == "não quero":
            etapa+=1
            print(f"{jogador2.nome} também tem flor mas não chamou {nome_etapas[etapa]}")
            distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
            return
        elif resposta["jogada"] == "contra flor":
            etapa+=1
            print(f"{jogador2.nome} pediu {nome_etapas[etapa]}")
            atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, False)
            resposta = input(f"Você aceita {nome_etapas[etapa]}? (s/n/aumentar): ").strip().lower()
            if resposta == 's':
                if jogador1.retornarPontosEnvido() > jogador2.retornarPontosEnvido():
                    print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                    distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                else:
                    print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                    distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                return
            elif resposta == 'n':
                print(f"{jogador1.nome} negou {nome_etapas[etapa]}")
                distribuir_pontos(jogo, 1, pontos_negados[etapa], False)
            elif resposta == 'aumentar':
                etapa+=1
                print(f"{jogador2.nome} pediu {nome_etapas[etapa]}")
                atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
                jogada_bot=jogador2.avaliarJogada(jogo.rodada_atual)
                if jogada_bot['jogada'] == 'quero':
                    if jogador1.retornarPontosEnvido() > jogador2.retornarPontosEnvido():
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                    else:
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                    return
                else:
                    print(f"{jogador2.nome} não quis {nome_etapas[etapa]}")
                    distribuir_pontos(jogo, 1, pontos_negados[etapa], False)
                    return



    elif quem_chamou == 2:  # Bot chamou
        print(f"{jogador2.nome} pediu {nome_etapas[etapa]}!")
        atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 2, False)
        if jogador1.checaFlor() == False:
            distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
            return
        
        resposta = input(f"Você quer {nome_etapas[etapa+1]}? (/n/aumentar): ").strip().lower()
        if resposta == "n":
            print(f"{jogador1.nome} tem flor também mas não quis aumentar para {nome_etapas[etapa]}")
            distribuir_pontos(jogo, 2, pontos_negados[etapa], False)
            return
        elif resposta == "aumentar":
            etapa+=1
            print(f"{jogador1.nome} pediu {nome_etapas[etapa]}!")
            atualizar_conhecimento_jogada_especial(nome_etapas[etapa], jogador2, jogo.rodada_atual, 1, False)
            resposta_bot = jogador2.avaliarJogada(jogo.rodada_atual)
            if resposta_bot["jogada"] == "quero":
                print(f"{jogador2.nome} aceitou {nome_etapas[etapa]}")
                if jogador1.retornarPontosEnvido() > jogador2.retornarPontosEnvido():
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                else:
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                return
            elif resposta_bot["jogada"] == "não quero":
                print(f"{jogador2.nome} não quis {nome_etapas[etapa]}")
                distribuir_pontos(jogo, 2, pontos_negados[etapa], False)
            elif resposta_bot["jogada"] == "contra flor resto":
                etapa+=1
                print(f"{jogador2.nome} pediu {nome_etapas[etapa]}!")
                resposta = input(f"Você aceita {nome_etapas[etapa]}? (s/n): ").strip().lower()
                if resposta == 's':
                    if jogador1.retornarPontosEnvido() > jogador2.retornarPontosEnvido():
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                    else:
                        print(f"{jogador1.nome} ganhou a {nome_etapas[etapa]}")
                        distribuir_pontos(jogo, 1, pontos_escala[etapa], False)
                    return
                else:
                    distribuir_pontos(jogo, 1, pontos_negados[etapa], False)



def atualizar_conhecimento_jogada_especial(jogada, jogador2, rodada, quem, negou):
    if jogada == 'envido':
        if negou:
            jogador2.atualizarRegistro(["quemNegouEnvido"], [quem])
        else:
            jogador2.atualizarRegistro(["quemPediuEnvido"], [quem])
    if jogada == 'real envido':
        if negou:
            jogador2.atualizarRegistro(["quemNegouRealEnvido"], [quem])
        else:
            jogador2.atualizarRegistro(["quemPediuRealEnvido"], [quem])
    if jogada == 'falta envido':
        if negou:
            jogador2.atualizarRegistro(["quemNegouFaltaEnvido"], [quem])
        else:
            jogador2.atualizarRegistro(["quemPediuFaltaEnvido"], [quem])
    if jogada == 'truco':
        if negou:
            jogador2.atualizarRegistro(["quemNegouTruco"], [quem])
        else:
            jogador2.atualizarRegistro(["quemTruco", "quandoTruco"], [quem, rodada])
    if jogada == 'retruco':
        if negou:
            jogador2.atualizarRegistro(["quemNegouTruco"], [quem])
        else:
            jogador2.atualizarRegistro(["quemRetruco", "quandoRetruco"], [quem, rodada])
    if jogada == 'vale quatro':
        if negou:
            jogador2.atualizarRegistro(["quemNegouTruco"], [quem])
        else:
            jogador2.atualizarRegistro(["quemValeQuatro", "quandoValeQuatro"], [quem, rodada])
    if jogada == 'flor':
        if negou:
            jogador2.atualizarRegistro(['quemNegouFlor'], [quem])
        else:
            jogador2.atualizarRegistro(['quemFlor'], [quem])
    if jogada == 'contra flor':
        if negou:
            jogador2.atualizarRegistro(['quemNegouFlor'], [quem])
        else:
            jogador2.atualizarRegistro(['quemContraFlor'], [quem])
    if jogada == 'contra flor resto':
        if negou:
            jogador2.atualizarRegistro(['quemNegouFlor'], [quem])
        else:
            jogador2.atualizarRegistro(['quemContraFlorResto'], [quem])




def inicializar_jogo():
    baralho = Baralho()
    baralho.criarBaralho()
    baralho.embaralhar()
    cbr = Cbr()
    jogo = Jogo()
    # nome_j1 = input("Nome Jogador 1: ")
    # nome_j2 = input("Nome Jogador 2: ")
    nome_j1 = "Luís Alvaro"
    nome_j2 = "Bot"
    jogador1 = jogo.criarJogador(nome_j1, baralho)
    jogador2 = jogo.criarBot(nome_j2, baralho, cbr)
    return jogo, baralho, jogador1, jogador2

def resetar_jogo(jogador1, jogador2, baralho, jogo):
    jogador1.resetar()
    jogador2.resetar()
    baralho.resetarBaralho()
    baralho.criarBaralho()
    baralho.embaralhar()
    jogador1.criarMao(baralho)
    jogador2.criarMao(baralho)
    jogo.resetarJogo()

def menu_jogador(jogador):
    print("\nSua mão: \n")
    jogador.mostrarMao()
    print("\n\n[0-2] Jogar carta  [4] Truco  [5] Retruco  [6] Vale quatro  [7] Envido  [8] Real envido  [9] Falta envido [10] Flor")
    while True:
        try:
            opcao = int(input("\nEscolha sua opção: "))
            if opcao in [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]:
                return opcao
        except ValueError:
            pass
        print("Opção inválida. Tente novamente.")

def confrontarEnvido(jogo, jogada, jogador1, jogador2):
    pontos_j1 = jogo.retornarPontosEnvido(jogador1.mao)
    pontos_j2 = jogo.retornarPontosEnvido(jogador2.mao)

    if pontos_j1 > pontos_j2:
        vencedor = 1
    elif pontos_j2 > pontos_j1:
        vencedor = 2
    elif pontos_j1 == pontos_j2:
        vencedor = jogo.jogador_mao

    jogador2.atualizarRegistro(['pontosEnvidoHumano'], [pontos_j1])

    if jogada == 'envido':
        pontos = 2
    elif jogada == 'real envido':
        pontos = 6
    elif jogada == 'falta envido':
        if vencedor == 1:
            pontos = jogo.pontos_maximos - jogo.pontos_j1
        elif vencedor == 2:
            pontos = jogo.pontos_maximos - jogo.pontos_j1

    if vencedor == 1:
        print(f"{jogador1.nome} ganhou o {jogada}")
        jogo.pontos_j1 += pontos
    elif vencedor == 2:
        print(f"{jogador2.nome} ganhou o {jogada}")
        jogo.pontos_j2 += pontos


def realizar_jogada(jogador, adversario, jogo, rodada, is_bot):
    carta = None
    if is_bot:
        jogada_bot = jogador.avaliarJogada(rodada)
        while jogada_bot['jogada'] != 'jogar carta':
            if jogada_bot['jogada'] == 'truco':
                resultado = escalonamento(0, 2, adversario, jogador, jogo, 'truco')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], True)
                    return None
            elif jogada_bot['jogada'] == 'retruco':
                resultado = escalonamento(1, 2, adversario, jogador, jogo, 'truco')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], True)
                    return None
            elif jogada_bot['jogada'] == 'vale quatro':
                resultado = escalonamento(2, 2, adversario, jogador, jogo, 'truco')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], True)
                    return None
            elif jogada_bot['jogada'] == 'envido':
                resultado = escalonamento(0, 2, adversario, jogador, jogo, 'envido')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], False)
                elif resultado['resultado'] == 'quero':
                    print("Envido aceito. Verificando ganhador.")
                    confrontarEnvido(jogo, resultado['jogada'], adversario, jogador)
                    
            elif jogada_bot['jogada'] == 'real envido':
                resultado = escalonamento(1, 2, adversario, jogador, jogo, 'envido')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], False)
                elif resultado['resultado'] == 'quero':
                    print("Real envido aceito. Verificando ganhador.")
                    confrontarEnvido(jogo, resultado['jogada'], adversario, jogador)
                    
            elif jogada_bot['jogada'] == 'falta envido':
                resultado = escalonamento(2, 2, adversario, jogador, jogo, 'envido')
                if resultado['resultado'] == 'não quero':
                    distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], False)
                elif resultado['resultado'] == 'quero':
                    print("Falta envido aceito. Verificando ganhador.")
                    confrontarEnvido(jogo, resultado['jogada'], adversario, jogador)

            elif jogada_bot['jogada'] == 'flor':
                escalonamento_flor(2, adversario, jogador, jogo)
                    
            jogada_bot = jogador.avaliarJogada(rodada)

        carta = jogada_bot['carta']
        print(f"{jogador.nome} jogou:")
        carta.printarCarta()

    elif not is_bot:
        while True:
            opcao = menu_jogador(jogador)
            if opcao <= 2:
                carta = jogador.jogarCarta(opcao)
                print(f"{jogador.nome} jogou:")
                carta.printarCarta()
                if jogo.rodada_atual == 1:
                    adversario.atualizarRegistro(["primeiraCartaHumano"], [carta.retornarPontosCarta(carta)])
                elif jogo.rodada_atual == 2:
                    adversario.atualizarRegistro(["segundaCartaHumano"], [carta.retornarPontosCarta(carta)])
                elif jogo.rodada_atual == 3:
                    adversario.atualizarRegistro(["terceiraCartaHumano"], [carta.retornarPontosCarta(carta)])
                break
            else:
                print(f"{jogador.nome} pediu: {opcoes_jogada[opcao - 4]}")
                if opcao <= 4 and opcao <= 6:
                    resultado = escalonamento(opcao - 4, 1, jogador, adversario, jogo, 'truco')
                    if resultado['resultado'] == 'não quero':
                        distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], True)
                        return None
                elif opcao >= 7 and opcao <= 9:
                    resultado = escalonamento(opcao-7, 1, jogador, adversario, jogo, 'envido')
                    if resultado['resultado'] == 'não quero':
                        distribuir_pontos(jogo, inverter_jogador(resultado['quem_negou']), resultado['pontos'], False)
                    elif resultado['resultado'] == 'quero':
                        print(f"{resultado['jogada'].capitalize()} aceito. Verificando ganhador.")
                        confrontarEnvido(jogo, resultado['jogada'], jogador, adversario)
                elif opcao == 10:
                    escalonamento_flor(1, jogador, adversario, jogo)
                    

    return carta

def inverter_jogador(jogador):
    if jogador == 1:
        return 2
    else:
        return 1

def distribuir_pontos(jogo, quem, pontos, encerrar_mao):
    if encerrar_mao:
        jogo.encerrar_mao = True
        jogo.truco_negado = True

    print(f"Distribuindo {pontos} para o jogador {quem}")
    
    if quem == 1:
        jogo.pontos_j1+=pontos
    if quem == 2:
        jogo.pontos_j2+=pontos

def verificar_ganhador(jogo):
    vencedor = None
    if not jogo.truco_negado:
        # Em caso da primeira rodada dar empate, a segunda decide o jogo
        if jogo.rodada_atual == 2 and jogo.rodadas_vencedor[0] == 3:
            if jogo.rodadas_vencedor[1] == 1:
                vencedor = 1
            if jogo.rodadas_vencedor[1] == 2:
                vencedor = 2

        # Se empatar a segunda, quem ganhou a primeira vence a mão
        if jogo.rodada_atual == 2 and jogo.rodadas_vencedor[1] == 3:
                if jogo.rodadas_vencedor[0] == 1:
                    vencedor = 1
                if jogo.rodadas_vencedor[0] == 2:
                    vencedor = 2

        # Em caso de empate na terceira rodada, vale a primeira 
        if jogo.rodada_atual == 3 and jogo.rodadas_vencedor[2] == 3:
                if jogo.rodadas_vencedor[0] == 1:
                    vencedor = 1
                if jogo.rodadas_vencedor[0] == 2:
                    vencedor = 2

        # Em caso de empate na primeira e segunda, a terceira decide a mão
        if jogo.rodada_atual == 3 and jogo.rodadas_vencedor[1] == 3 and jogo.rodadas_vencedor[0] == 3:
                if jogo.rodadas_vencedor[2] == 1:
                    vencedor = 1
                if jogo.rodadas_vencedor[2] == 2:
                    vencedor = 2

        # Ou vence quem tiver mais rodadas
        if jogo.rodada_atual >= 2 and vencedor == None:
            if jogo.rodadas_vencedor.count(1) > jogo.rodadas_vencedor.count(2) and jogo.rodadas_vencedor.count(1) == 2:
                vencedor = 1
            elif jogo.rodadas_vencedor.count(2) > jogo.rodadas_vencedor.count(1) and  jogo.rodadas_vencedor.count(2) == 2:
                vencedor = 2

        # Soma os pontos ao jogador ganhador e encerra a mão
        if vencedor == 1:
            print(f"Jogador 1 ganhou {jogo.pontos_mao} pontos")
            jogo.encerrar_mao = True
            jogo.pontos_j1+=jogo.pontos_mao
        elif vencedor == 2:
            print(f"Jogador 2 ganhou {jogo.pontos_mao} pontos")
            jogo.encerrar_mao = True
            jogo.pontos_j2+=jogo.pontos_mao

    if jogo.encerrar_mao or jogo.rodada_atual == 3:
        jogo.jogador_mao = inverter_jogador(jogo.jogador_mao)
        print(f"Saldo atual de pontos: \nPontos jogador 1: {jogo.pontos_j1}\nPontos jogador 2: {jogo.pontos_j2}\nJogo vai até {jogo.pontos_maximos}")

    if jogo.pontos_j1 >= jogo.pontos_maximos or jogo.pontos_j2 >= jogo.pontos_maximos:
        jogo.encerrar_jogo = True
        if jogo.pontos_j1 > jogo.pontos_j2:
            print(f"Jogador 1 é o ganhador! Reinciando jogo.")
        if jogo.pontos_j2 > jogo.pontos_j1:
            print(f"Jogador 2 é o ganhador! Reinciando jogo.")
            

def processar_rodada(jogo, jogador1, jogador2, rodada_atual):
    if jogo.encerrar_mao:
        return
    rodada = jogo.rodada_atual = rodada_atual
    print(f"\n--- Rodada {rodada} ---")

    if jogo.quemJogaPrimeiro == 2:
        print("\nSua mão\n")
        jogador1.mostrarMao()

    if jogo.quemJogaPrimeiro == 1:
        ordem = [(jogador1, jogador2, False), (jogador2, jogador1, True)]
    else:
        ordem = [(jogador2, jogador1, True), (jogador1, jogador2, False)]

    cartas = []
    for jogador, adversario, is_bot in ordem:
        carta = realizar_jogada(jogador, adversario, jogo, rodada, is_bot)
        if carta is None:
            print("Rodada encerrada.")
            verificar_ganhador(jogo)
            return
        cartas.append(carta)

    carta1, carta2 = cartas

    if jogo.quemJogaPrimeiro == 2:
        carta1, carta2 = carta2, carta1

    ganhador = jogo.verificarCartaVencedora(carta1, carta2)

    if rodada == 1:
        rodada_str = "Primeira"
    elif rodada == 2:
        rodada_str = "Segunda"
    else:
        rodada_str = "Terceira"

    if ganhador == "Empate":
        print("Empate")
        jogo.rodadas_vencedor[rodada - 1] = 3
        jogo.quemJogaPrimeiro = jogo.jogador_mao
        jogador2.atualizarRegistro(["ganhador"+rodada_str+"Rodada"], [0])
    elif ganhador == carta1:
        print(f"{jogador1.nome} ganhou a rodada")
        jogo.rodadas_vencedor[rodada - 1] = 1
        jogo.quemJogaPrimeiro = 1
        jogador2.atualizarRegistro(["ganhador"+rodada_str+"Rodada"], [1])
    elif ganhador == carta2:
        print(f"{jogador2.nome} ganhou a rodada")
        jogo.rodadas_vencedor[rodada - 1] = 2
        jogo.quemJogaPrimeiro = 2
        jogador2.atualizarRegistro(["ganhador"+rodada_str+"Rodada"], [2])

    print(jogo.rodadas_vencedor)
    # Condição para verificar ganhador da mão (implementar depois)
    verificar_ganhador(jogo)
    # Adicionar lógica para caso o bot jogue primeiro, se necessário

def main():
    jogo, baralho, jogador1, jogador2 = inicializar_jogo()
    while not jogo.encerrar_jogo:
        resetar_jogo(jogador1, jogador2, baralho, jogo)
        processar_rodada(jogo, jogador1, jogador2, 1)
        processar_rodada(jogo, jogador1, jogador2, 2)
        processar_rodada(jogo, jogador1, jogador2, 3)

if __name__ == '__main__':
    main()
