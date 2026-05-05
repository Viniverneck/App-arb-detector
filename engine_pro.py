import time

def calcular_soma_prob(o1, o2):
    return (1/o1) + (1/o2)

def detectar_arb(o1, o2):
    soma = calcular_soma_prob(o1, o2)
    return soma < 1, (1 - soma) * 100

def prever_movimento(o1, o2):
    try:
        alvo = 1 / (1 - (1 / o1))
        falta = alvo - o2
    except:
        return None

    if falta < 0.05:
        return "IMINENTE"
    if falta < 0.15:
        return "APROXIMANDO"
    return None

def score(o1, o2, delta1, delta2):
    s = 0

    # proximidade
    s += max(0, 2 - abs(o1 - o2))

    # movimento (isso é o ouro)
    if delta1 > 0 and delta2 < 0:
        s += 2
    if delta2 > 0 and delta1 < 0:
        s += 2

    return round(s, 2)