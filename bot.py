import json
import html
import requests
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ARQUIVO_JOGOS = "jogos.json"
LIMITE_TELEGRAM = 3500


def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    partes = dividir_mensagem(texto)

    for parte in partes:
        payload = {
            "chat_id": CHAT_ID,
            "text": parte,
            "parse_mode": "HTML"
        }

        resposta = requests.post(url, json=payload)

        if resposta.status_code == 200:
            print("Mensagem enviada com sucesso!")
        else:
            print("Erro ao enviar mensagem:")
            print(resposta.text)


def dividir_mensagem(texto):
    linhas = texto.split("\n")
    partes = []
    parte_atual = ""

    for linha in linhas:
        if len(parte_atual) + len(linha) + 1 > LIMITE_TELEGRAM:
            partes.append(parte_atual)
            parte_atual = linha + "\n"
        else:
            parte_atual += linha + "\n"

    if parte_atual.strip():
        partes.append(parte_atual)

    return partes


def carregar_jogos():
    try:
        with open(ARQUIVO_JOGOS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(f"Erro: arquivo {ARQUIVO_JOGOS} não encontrado.")
        return {}
    except json.JSONDecodeError:
        print("Erro: o arquivo jogos.json está com problema de formatação.")
        return {}


def montar_mensagem(jogos_por_categoria):
    hoje = datetime.now().strftime("%d/%m/%Y")

    mensagem = f"🔥 <b>RADAR LUKA — {hoje}</b>\n"
    mensagem += "\n📌 <b>Jogos candidatos para procurar odds manualmente</b>\n"

    for categoria, jogos in jogos_por_categoria.items():
        mensagem += f"\n<b>{html.escape(categoria)}</b>\n"

        if not jogos:
            mensagem += "• Nenhum jogo cadastrado\n"
        else:
            for jogo in jogos:
                mensagem += f"• {html.escape(jogo)}\n"

    mensagem += "\n⚠️ <b>Regra:</b> confirmar odds na bet antes de entrar."
    mensagem += "\n📩 Depois mandar as odds aqui para montar simples, duplas e stakes."

    return mensagem


jogos = carregar_jogos()

if jogos:
    mensagem_final = montar_mensagem(jogos)
    enviar_telegram(mensagem_final)
else:
    print("Nenhuma mensagem enviada porque não há jogos carregados.")