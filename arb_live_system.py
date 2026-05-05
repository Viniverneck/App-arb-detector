import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="ARB Scanner PRO", layout="wide")

st.title("⚡ ARB Scanner PRO (Live + Previsão)")

# -----------------------------------
# CONFIG
# -----------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    valor_base = st.number_input("💰 Stake base (R$)", 10.0, 10000.0, 100.0)

    odd_min = st.slider("Odd mínima", 1.5, 3.0, 1.8, 0.05)
    diff_max = st.slider("Diferença máxima", 0.1, 2.0, 1.0, 0.1)

    auto_refresh = st.toggle("🔄 Auto-refresh", value=False)

    intervalo = st.select_slider(
        "Intervalo (segundos)",
        options=[2, 5, 10],
        value=5
    )

# -----------------------------------
# DETECTOR
# -----------------------------------
def detectar_arb(odd1, odd2):
    if odd1 < odd_min or odd2 < odd_min:
        return None

    if abs(odd1 - odd2) > diff_max:
        return None

    soma = (1/odd1) + (1/odd2)
    lucro = (1 - soma) * 100

    if soma < 1:
        status = "🚨 ARB"
    elif soma < 1.02:
        status = "🔥 QUASE"
    else:
        status = "👀"

    return soma, lucro, status

# -----------------------------------
# PREVISÃO (ANTES DA ARB)
# -----------------------------------
def prever_arb(odd1, odd2):
    try:
        alvo_2 = 1 / (1 - (1 / odd1))
        falta_2 = alvo_2 - odd2
    except:
        alvo_2, falta_2 = None, None

    return alvo_2, falta_2

# -----------------------------------
# STAKES
# -----------------------------------
def calcular_stakes(odd1, odd2, valor):
    soma = (1/odd1) + (1/odd2)

    if soma >= 1:
        return None

    retorno = valor / soma

    stake1 = retorno / odd1
    stake2 = retorno / odd2

    lucro = retorno - (stake1 + stake2)

    return round(stake1,2), round(stake2,2), round(lucro,2)

# -----------------------------------
# SIMULADOR (DADOS FAKE PARA TESTE)
# -----------------------------------
def gerar_jogos():
    jogos = []
    for i in range(15):
        o1 = round(1.7 + i*0.05, 2)
        o2 = round(1.7 + (14-i)*0.05, 2)

        jogos.append({
            "jogo": f"Time {i} x Time {i+1}",
            "odd1": o1,
            "odd2": o2
        })
    return jogos

# -----------------------------------
# EXECUÇÃO
# -----------------------------------
dados = gerar_jogos()

rows = []

for d in dados:
    r = detectar_arb(d["odd1"], d["odd2"])

    if not r:
        continue

    soma, lucro, status = r
    alvo, falta = prever_arb(d["odd1"], d["odd2"])

    rows.append({
        "Jogo": d["jogo"],
        "Odd Casa": d["odd1"],
        "Odd Fora": d["odd2"],
        "Lucro %": round(lucro,2),
        "Status": status,
        "Falta p/ ARB": round(falta,3) if falta else None
    })

df = pd.DataFrame(rows).sort_values("Lucro %", ascending=False)

# -----------------------------------
# TABELA
# -----------------------------------
st.dataframe(df, use_container_width=True)

# -----------------------------------
# DETALHES
# -----------------------------------
st.subheader("📌 Execução")

for _, row in df.head(5).iterrows():
    with st.expander(f"{row['Jogo']} | {row['Status']} | {row['Lucro %']}%"):

        odd1 = row["Odd Casa"]
        odd2 = row["Odd Fora"]

        stakes = calcular_stakes(odd1, odd2, valor_base)

        if stakes:
            s1, s2, lucro = stakes

            st.success(f"💰 Lucro garantido: R$ {lucro}")
            st.write(f"Apostar:")
            st.write(f"Casa → R$ {s1}")
            st.write(f"Fora → R$ {s2}")

        else:
            st.warning("Ainda não é arbitragem — mas está perto")

# -----------------------------------
# AUTO REFRESH (SAFE iOS)
# -----------------------------------
if auto_refresh:
    time.sleep(intervalo)
    st.rerun()