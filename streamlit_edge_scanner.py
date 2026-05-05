import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="EDGE SCANNER", layout="wide")
st.title("🧠 EDGE SCANNER — Arbitragem Antecipada")

# -----------------------------------
# CONFIG
# -----------------------------------
with st.sidebar:
    st.header("⚙️ Config")

    valor = st.number_input("💰 Stake", 10.0, 10000.0, 100.0)
    sens = st.slider("Sensibilidade", 0.5, 2.0, 1.0)

    auto = st.toggle("Auto-refresh", True)
    intervalo = st.select_slider("Intervalo", [2,5,10], 5)

# -----------------------------------
# MEMÓRIA
# -----------------------------------
if "hist" not in st.session_state:
    st.session_state["hist"] = {}

# -----------------------------------
# SIMULAÇÃO (troca por API depois)
# -----------------------------------
def gerar_dados():
    jogos = []
    for i in range(12):
        base = random.uniform(1.8, 2.4)
        drift = random.uniform(-0.12, 0.12)

        o1 = round(base + drift, 2)
        o2 = round((2.8 - base) - drift, 2)

        jogos.append({
            "id": i,
            "jogo": f"Jogo {i}",
            "o1": max(1.5, o1),
            "o2": max(1.5, o2)
        })
    return jogos

# -----------------------------------
# EDGE DETECTOR (O OURO)
# -----------------------------------
def detectar_edge(id_jogo, o1, o2):
    hist = st.session_state["hist"]

    if id_jogo not in hist:
        hist[id_jogo] = {"o1": o1, "o2": o2}
        return None

    old1 = hist[id_jogo]["o1"]
    old2 = hist[id_jogo]["o2"]

    # atualiza histórico
    hist[id_jogo] = {"o1": o1, "o2": o2}

    d1 = o1 - old1
    d2 = o2 - old2

    soma = (1/o1) + (1/o2)

    # -------------------------
    # EDGE CONDITIONS
    # -------------------------

    score = 0

    # 1. movimento oposto (FORTÍSSIMO)
    if d1 > 0 and d2 < 0:
        score += 3
    if d2 > 0 and d1 < 0:
        score += 3

    # 2. convergência
    score += max(0, 2 - abs(o1 - o2))

    # 3. proximidade de arb
    gap = soma - 1
    if gap < 0.03:
        score += 2
    elif gap < 0.06:
        score += 1

    # 4. filtro de qualidade
    if o1 < 1.7 or o2 < 1.7:
        return None

    # classificação
    if soma < 1:
        status = "🚨 ARB"
    elif gap < 0.02:
        status = "🔥 ENTRAR AGORA"
    elif gap < 0.05:
        status = "⚡ PRE-ARB"
    else:
        status = None

    if score < 3:
        return None

    return {
        "o1": o1,
        "o2": o2,
        "d1": round(d1,3),
        "d2": round(d2,3),
        "score": round(score,2),
        "status": status,
        "gap": round(gap,4)
    }

# -----------------------------------
# STAKE
# -----------------------------------
def calc_stake(o1, o2, v):
    soma = (1/o1)+(1/o2)
    if soma >= 1:
        return None

    r = v / soma
    s1 = r / o1
    s2 = r / o2
    lucro = r - (s1+s2)

    return round(s1,2), round(s2,2), round(lucro,2)

# -----------------------------------
# EXECUÇÃO
# -----------------------------------
dados = gerar_dados()

rows = []

for d in dados:
    e = detectar_edge(d["id"], d["o1"], d["o2"])
    if not e:
        continue

    rows.append({
        "Jogo": d["jogo"],
        "Casa": e["o1"],
        "Fora": e["o2"],
        "Δ Casa": e["d1"],
        "Δ Fora": e["d2"],
        "Score": e["score"],
        "Gap": e["gap"],
        "Status": e["status"]
    })

df = pd.DataFrame(rows).sort_values("Score", ascending=False)

# -----------------------------------
# TABELA
# -----------------------------------
st.dataframe(df, use_container_width=True)

# -----------------------------------
# EXECUÇÃO
# -----------------------------------
st.subheader("🎯 Oportunidades")

for _, r in df.head(5).iterrows():
    with st.expander(f"{r['Jogo']} | {r['Status']} | Score {r['Score']}"):

        stakes = calc_stake(r["Casa"], r["Fora"], valor)

        if stakes:
            s1,s2,l = stakes
            st.success(f"💰 Lucro: R$ {l}")
            st.write(f"Apostar {s1} / {s2}")
        else:
            st.warning("Ainda não é arb — mas é EDGE")

# -----------------------------------
# AUTO REFRESH
# -----------------------------------
if auto:
    time.sleep(intervalo)
    st.rerun()
