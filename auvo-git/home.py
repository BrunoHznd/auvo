import streamlit as st
import time
import os
import base64
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Carregando...",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Caminho para a imagem do foguete
gif_path = Path("foguete.gif")

# Verifica se o arquivo existe
if not gif_path.exists():
    st.error(f"Arquivo não encontrado: {gif_path}")
    st.stop()

# Codifica a imagem em base64
encoded_gif = get_base64_of_bin_file(gif_path)

# CSS personalizado para a animação do foguete
st.markdown(
    """
    <style>
        @keyframes takeoff {
            /* Subida */
            0% {
                transform: translateX(-50%) rotate(0deg) scale(0.5);
                bottom: 20px;  /* Pouso um pouco mais alto */
                opacity: 1;
                filter: brightness(1);
            }
            40% {
                transform: translateX(-50%) rotate(0deg) scale(0.7);
                bottom: calc(100% - 150px);  /* Vai até 150px do topo */
                opacity: 1;
                filter: brightness(1.5) drop-shadow(0 0 15px #ff6600);
            }
            /* Desce mais um pouco no topo */
            50% {
                bottom: calc(100% - 200px);  /* Desce até 200px do topo */
            }
            /* Pausa no topo */
            50.1%, 60% {
                transform: translateX(-50%) rotate(0deg) scale(0.7);
                bottom: calc(100% - 200px);
                opacity: 1;
                filter: brightness(1.5) drop-shadow(0 0 15px #ff6600);
            }
            /* Início da descida com rotação */
            60.1% {
                transform: translateX(-50%) rotate(0deg) scale(0.7);
                bottom: calc(100% - 200px);
                opacity: 1;
                filter: brightness(1.5) drop-shadow(0 0 15px #ff6600);
            }
            90% {
                transform: translateX(-50%) rotate(360deg) scale(0.7);
                bottom: 25%;
                opacity: 1;
                filter: brightness(1.3) drop-shadow(0 0 10px #ff6600);
            }
            /* Final da descida */
            100% {
                transform: translateX(-50%) rotate(360deg) scale(0.6);
                bottom: 20px;  /* Pouso um pouco mais alto */
                opacity: 0.9;
                filter: brightness(1) drop-shadow(0 0 5px #ff6600);
            }
        }
        
        .rocket-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-end;
            pointer-events: none;
            z-index: 9999;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        
        .rocket {
            width: 100px;
            height: 100px;
            animation: takeoff 12s ease-in-out forwards;
            position: absolute;
            bottom: -50px;
            left: 50%;
            transform-origin: center;
            transform-style: preserve-3d;
            backface-visibility: visible;
            transition: all 0.3s ease;
            transform: translateX(-50%) rotate(0deg);
        }
        
        .countdown {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 32px;
            color: #3498db;
            font-weight: bold;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        body {
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# HTML para o foguete e contagem regressiva
st.markdown(
    f"""
    <div class="rocket-container">
        <img src="data:image/gif;base64,{encoded_gif}" class="rocket" alt="Foguete decolando">
    </div>
    <div class="countdown" id="countdown">12</div>
    """,
    unsafe_allow_html=True
)

# JavaScript para a contagem regressiva
st.components.v1.html(
    """
    <script>
    let count = 12;
    const countdown = document.getElementById('countdown');
    
    const timer = setInterval(() => {
        count--;
        countdown.textContent = count;
        
        if (count <= 0) {
            clearInterval(timer);
            // Redireciona para o dashboard após a animação
            setTimeout(() => {
                window.location.href = 'dashboard_mapa';
            }, 1000);
        }
    }, 1000);
    </script>
    """,
    height=0
)

# Aguarda 12 segundos (tempo total da animação + atraso)
time.sleep(12)