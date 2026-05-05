import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Detector de Arbitragem", layout="wide")

st.title("⚡ Detector de Arbitragem (Live + Previsão)")

# -----------------------------
# CONFIG
# -----------------------------
valor_base = st.number_input("💰 Valor base (R$)", 10.0, 10000.0, 100.0, 10.0)

odd_min = st.slider("Odd mínima", 1.5, 3.0, 1.8, 0.05)
diff_max = st.slider("Diferença máxima entre odds", 0.1, 2.0, 1.0, 0.1)

# -----------------------------
# DETECTOR PRINCIPAL
# -----------------------------
def detectar_arb(odd1, odd2):
    try:
        odd1 = float(odd1)
        odd2 = float(odd2)
    except:
        return None

    # Filtro estilo trader
    if odd1 < odd_min or odd2 < odd_min:
        return None

    if abs(odd1 - odd2) > diff_max:
        return None

    soma = (1 / odd1) + (1 / odd2)
    lucro_pct = (1 - soma) * 100

    if soma < 1:
        status = "🚨 ARB REAL"
    elif soma < 1.02:
        status = "🔥 QUASE ARB"
    else:
        status = "👀 MONITORAR"

    return {
        "odd1": odd1,
        "odd2": odd2,
        "soma": soma,
        "lucro_pct": round(lucro_pct, 2),
        "status": status
    }

# -----------------------------
# PREVISÃO DE ARB (NOVA)
# -----------------------------
def prever_arb(odd1, odd2):
    """
    Estima quanto a odd precisa mover pra virar arbitragem
    """
    try:
        odd1 = float(odd1)
        odd2 = float(odd2)
    except:
        return None

    # Qual odd precisa subir
    alvo_odd2 = 1 / (1 - (1 / odd1)) if odd1 > 1 else None
    alvo_odd1 = 1 / (1 - (1 / odd2)) if odd2 > 1 else None

    falta_odd2 = None
    falta_odd1 = None

    if alvo_odd2:
        falta_odd2 = round(alvo_odd2 - odd2, 3)

    if alvo_odd1:
        falta_odd1 = round(alvo_odd1 - odd1, 3)

    return {
        "alvo_odd1": round(alvo_odd1, 3) if alvo_odd1 else None,
        "alvo_odd2": round(alvo_odd2, 3) if alvo_odd2 else None,
        "falta_odd1": falta_odd1,
        "falta_odd2": falta_odd2
    }

# -----------------------------
# CALCULO DE STAKES
# -----------------------------
def calcular_stakes(odd1, odd2, valor):
    soma = (1/odd1) + (1/odd2)

    if soma >= 1:
        return None

    retorno = valor / soma

    stake1 = retorno / odd1
    stake2 = retorno / odd2

    lucro = retorno - (stake1 + stake2)

    return {
        "stake1": round(stake1, 2),
        "stake2": round(stake2, 2),
        "lucro": round(lucro, 2)
    }

# -----------------------------
# INPUT MANUAL
# -----------------------------
st.subheader("🔎 Teste manual")

col1, col2 = st.columns(2)

odd1 = col1.number_input("Odd Casa", 1.01, 10.0, 2.00)
odd2 = col2.number_input("Odd Fora", 1.01, 10.0, 2.00)

resultado = detectar_arb(odd1, odd2)
previsao = prever_arb(odd1, odd2)

if resultado:
    st.markdown(f"### {resultado['status']}")
    st.write(f"Lucro: {resultado['lucro_pct']}%")

    stakes = calcular_stakes(odd1, odd2, valor_base)

    if stakes:
        st.success(f"💰 Lucro garantido: R$ {stakes['lucro']}")
        st.write(f"Apostar R$ {stakes['stake1']} e R$ {stakes['stake2']}")

if previsao:
    st.info("📊 Previsão de arbitragem")

    st.write(f"Odd 1 precisa ir para: {previsao['alvo_odd1']}")
    st.write(f"Odd 2 precisa ir para: {previsao['alvo_odd2']}")

    st.write(f"Falta mover: {previsao['falta_odd1']} / {previsao['falta_odd2']}")

# -----------------------------
# SIMULADOR EM MASSA
# -----------------------------
st.subheader("📊 Simulação rápida")

dados = []
for o1 in [1.8, 2.0, 2.2, 2.5]:
    for o2 in [1.8, 2.0, 2.2, 2.5]:
        r = detectar_arb(o1, o2)
        if r:
            dados.append({
                "Odd1": o1,
                "Odd2": o2,
                "Lucro %": r["lucro_pct"],
                "Status": r["status"]
            })

if dados:
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True)
