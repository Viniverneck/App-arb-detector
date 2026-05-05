import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="ARB Predictor PRO", layout="wide")

st.title("🧠 ARB Predictor PRO (Antecipação de Arbitragem)")

# -----------------------------------
# CONFIG
# -----------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    valor_base = st.number_input("💰 Stake base (R$)", 10.0, 10000.0, 100.0)

    sensibilidade = st.slider(
        "🎯 Sensibilidade (detectar antes)",
        0.5, 2.0, 1.0, 0.1,
        help="Quanto menor, mais cedo detecta oportunidades"
    )

    auto_refresh = st.toggle("🔄 Auto-refresh", value=True)

    intervalo = st.select_slider(
        "Intervalo (segundos)",
        options=[2, 5, 10],
        value=5
    )

# -----------------------------------
# ESTADO (memória das odds)
# -----------------------------------
if "historico" not in st.session_state:
    st.session_state["historico"] = {}

# -----------------------------------
# SIMULAÇÃO DE MERCADO (substituível por API depois)
# -----------------------------------
def gerar_odds():
    jogos = []

    for i in range(10):
        base = random.uniform(1.7, 2.5)

        # simula movimento real (uma sobe, outra desce)
        drift = random.uniform(-0.1, 0.1)

        odd1 = round(base + drift, 2)
        odd2 = round((2.8 - base) - drift, 2)

        jogos.append({
            "id": i,
            "jogo": f"Time {i} x Time {i+1}",
            "odd1": max(1.5, odd1),
            "odd2": max(1.5, odd2)
        })

    return jogos

# -----------------------------------
# DETECTOR PRINCIPAL
# -----------------------------------
def detectar_movimento(id_jogo, odd1, odd2):
    hist = st.session_state["historico"]

    if id_jogo not in hist:
        hist[id_jogo] = {"odd1": odd1, "odd2": odd2}
        return None

    old1 = hist[id_jogo]["odd1"]
    old2 = hist[id_jogo]["odd2"]

    # salvar novo estado
    hist[id_jogo] = {"odd1": odd1, "odd2": odd2}

    delta1 = odd1 - old1
    delta2 = odd2 - old2

    return delta1, delta2

# -----------------------------------
# PREVISÃO DE ARB
# -----------------------------------
def prever_arb(odd1, odd2):
    soma = (1/odd1) + (1/odd2)

    # já é arb
    if soma < 1:
        return "🚨 ARB AGORA", (1 - soma) * 100

    # previsão
    alvo = 1 / (1 - (1 / odd1))
    falta = alvo - odd2

    if falta < 0.05 * sensibilidade:
        return "🔥 IMINENTE", None

    if falta < 0.15 * sensibilidade:
        return "⚡ APROXIMANDO", None

    return None, None

# -----------------------------------
# SCORE INTELIGENTE
# -----------------------------------
def score_oportunidade(odd1, odd2, delta1, delta2):
    score = 0

    # odds equilibradas
    score += max(0, 2 - abs(odd1 - odd2))

    # movimento forte
    if delta1 and delta2:
        if delta1 > 0 and delta2 < 0:
            score += 2
        if delta2 > 0 and delta1 < 0:
            score += 2

    return round(score, 2)

# -----------------------------------
# STAKES
# -----------------------------------
def calcular_stakes(odd1, odd2, valor):
    soma = (1/odd1) + (1/odd2)

    if soma >= 1:
        return None

    retorno = valor / soma

    s1 = retorno / odd1
    s2 = retorno / odd2
    lucro = retorno - (s1 + s2)

    return round(s1,2), round(s2,2), round(lucro,2)

# -----------------------------------
# EXECUÇÃO
# -----------------------------------
dados = gerar_odds()

rows = []

for d in dados:
    move = detectar_movimento(d["id"], d["odd1"], d["odd2"])

    if not move:
        continue

    delta1, delta2 = move

    status, lucro_real = prever_arb(d["odd1"], d["odd2"])

    score = score_oportunidade(d["odd1"], d["odd2"], delta1, delta2)

    if not status:
        continue

    rows.append({
        "Jogo": d["jogo"],
        "Odd Casa": d["odd1"],
        "Odd Fora": d["odd2"],
        "Δ Casa": round(delta1,3),
        "Δ Fora": round(delta2,3),
        "Status": status,
        "Score": score,
        "Lucro %": round(lucro_real,2) if lucro_real else None
    })

df = pd.DataFrame(rows).sort_values("Score", ascending=False)

# -----------------------------------
# TABELA
# -----------------------------------
st.dataframe(df, use_container_width=True)

# -----------------------------------
# EXECUÇÃO DETALHADA
# -----------------------------------
st.subheader("🎯 Entradas Prioritárias")

for _, row in df.head(5).iterrows():
    with st.expander(f"{row['Jogo']} | {row['Status']} | Score {row['Score']}"):

        odd1 = row["Odd Casa"]
        odd2 = row["Odd Fora"]

        stakes = calcular_stakes(odd1, odd2, valor_base)

        if stakes:
            s1, s2, lucro = stakes
            st.success(f"💰 Lucro: R$ {lucro}")
            st.write(f"Apostar: {s1} / {s2}")
        else:
            st.warning("Ainda não é arb — oportunidade antecipada")

# -----------------------------------
# AUTO REFRESH
# -----------------------------------
if auto_refresh:
    time.sleep(intervalo)
    st.rerun()