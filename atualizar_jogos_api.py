import json
import re
import requests
import unicodedata
from datetime import datetime
import os

try:
    from config import API_FOOTBALL_KEY as LOCAL_API_KEY
except Exception:
    LOCAL_API_KEY = ""

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", LOCAL_API_KEY)

ARQUIVO_JOGOS = "jogos.json"
URL_FIXTURES = "https://v3.football.api-sports.io/fixtures"

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}


# ============================================================
# TIMES FORTES / OFENSIVOS PARA CANTOS E BUILDERS
# ============================================================

FAVORITOS_CANTOS = [
    "Manchester City",
    "Manchester United",
    "Liverpool",
    "Arsenal",
    "Chelsea",
    "Tottenham",
    "Newcastle",

    "Bayern Munich",
    "Bayern München",
    "Borussia Dortmund",
    "RB Leipzig",
    "Bayer Leverkusen",

    "Real Madrid",
    "Barcelona",
    "Atletico Madrid",
    "Atlético Madrid",

    "Paris Saint Germain",
    "PSG",
    "Marseille",
    "Lyon",
    "Monaco",

    "Benfica",
    "Sporting CP",
    "Sporting Lisbon",
    "FC Porto",
    "Porto",

    "Ajax",
    "PSV Eindhoven",
    "Feyenoord",

    "Club Brugge",
    "Anderlecht",

    "Galatasaray",
    "Fenerbahce",
    "Fenerbahçe",
    "Besiktas",
    "Beşiktaş",

    "Juventus",
    "Inter",
    "Inter Milan",
    "Internazionale",
    "AC Milan",
    "Napoli",
    "Roma",
    "Lazio",

    "Flamengo",
    "Palmeiras",
    "Botafogo",
    "Fluminense",
    "São Paulo",
    "Sao Paulo",
    "Corinthians",
    "Atlético Mineiro",
    "Atletico Mineiro",
    "Cruzeiro",
    "Grêmio",
    "Gremio",
    "Internacional",

    "Inter Miami",
    "Los Angeles FC",
    "LAFC",
    "Columbus Crew",
    "Cincinnati"
]


# ============================================================
# JOGADORES ESPECIAIS — ESTRATÉGIA C
# ============================================================

TIMES_JOGADORES_ESPECIAIS = {
    "Manchester City": [
        "Haaland marcar + Doku assistência",
        "Haaland marcar + Cherki assistência",
        "Haaland cabeça"
    ],
    "Bayern Munich": [
        "Kane marcar + Olise assistência",
        "Musiala assistência + Kane marcar",
        "Kane cabeça",
        "Olise fora da área"
    ],
    "Bayern München": [
        "Kane marcar + Olise assistência",
        "Musiala assistência + Kane marcar",
        "Kane cabeça",
        "Olise fora da área"
    ],
    "Inter Miami": [
        "Messi assistência + atacante marcar",
        "Messi fora da área",
        "Messi 1+ chute no alvo + Miami gols"
    ],
    "Liverpool": [
        "Van Dijk cabeça",
        "Szoboszlai assistência + Van Dijk cabeça",
        "Mac Allister fora da área"
    ],
    "Manchester United": [
        "Bruno Fernandes fora da área",
        "Bruno assistência + atacante marcar"
    ],
    "Flamengo": [
        "Pedro marcar",
        "Pedro 1+ chute no alvo + Flamengo domínio",
        "Arrascaeta assistência + Pedro marcar"
    ],
    "Inter": [
        "Lautaro marcar",
        "Lautaro 1+ chute no alvo + Inter domínio"
    ],
    "Inter Milan": [
        "Lautaro marcar",
        "Lautaro 1+ chute no alvo + Inter domínio"
    ],
    "Internazionale": [
        "Lautaro marcar",
        "Lautaro 1+ chute no alvo + Inter domínio"
    ]
}


# ============================================================
# FUNÇÕES DE TEXTO
# ============================================================

def normalizar(texto):
    if not texto:
        return ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def eh_sub_ou_reserva(nome):
    """
    Bloqueia:
    - U18, U19, U20, U21, U23
    - Sub-18, Sub-20 etc.
    - Under 20 etc.
    - Youth / Academy / Reserves
    - Time B no final
    - Time II / III no final
    """
    n = normalizar(nome)

    if re.search(r"\bu(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    if re.search(r"\bsub[- ]?(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    if re.search(r"\bunder[- ]?(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    termos_reserva = [
        "youth",
        "academy",
        "reserve",
        "reserves",
        "jong "
    ]

    for termo in termos_reserva:
        if termo in n:
            return True

    # Exemplo: Porto B, Sporting CP B
    if re.search(r"\bb\b$", n):
        return True

    # Exemplo: Real Madrid II, Winterthur II
    if re.search(r"\bii\b$", n):
        return True

    if re.search(r"\biii\b$", n):
        return True

    return False


def jogo_bloqueado(casa, visitante, liga):
    if eh_sub_ou_reserva(casa):
        return True

    if eh_sub_ou_reserva(visitante):
        return True

    if eh_sub_ou_reserva(liga):
        return True

    return False


def eh_time_exato(nome_time, referencia):
    return normalizar(nome_time) == normalizar(referencia)


def eh_favorito(nome_time):
    for favorito in FAVORITOS_CANTOS:
        if eh_time_exato(nome_time, favorito):
            return True
    return False


def adicionar_sem_duplicar(lista, item):
    if item not in lista:
        lista.append(item)


# ============================================================
# FILTRO DE CARTÕES
# ============================================================

def eh_liga_cartoes(liga, pais):
    liga_n = normalizar(liga)
    pais_n = normalizar(pais)

    # Bloqueia feminino para cartões
    termos_feminino = [
        "women",
        "woman",
        "feminina",
        "femenina",
        "feminino",
        "femenino",
        "liga f",
        "primera division femenina",
        "serie a women",
        "super league women"
    ]

    for termo in termos_feminino:
        if termo in liga_n:
            return False

    # Bloqueia divisões muito baixas / regionais para cartões
    termos_baixos = [
        "tercera",
        "quarta",
        "regional",
        "state",
        "district",
        "county",
        "amateur",
        "rfef",
        "provincial",
        "tasmania",
        "victoria premier league",
        "queensland premier league",
        "npl",
        "northern championship",
        "southern championship"
    ]

    for termo in termos_baixos:
        if termo in liga_n:
            return False

    # Competições continentais boas para cartões
    ligas_especiais = [
        "libertadores",
        "sudamericana",
        "copa do brasil",
        "champions league",
        "europa league",
        "conference league"
    ]

    for termo in ligas_especiais:
        if termo in liga_n:
            return True

    # Ligas permitidas por país
    ligas_por_pais = {
        "brazil": [
            "serie a",
            "serie b",
            "copa do brasil"
        ],
        "spain": [
            "la liga",
            "segunda división",
            "segunda division"
        ],
        "italy": [
            "serie a",
            "serie b",
            "coppa italia"
        ],
        "england": [
            "premier league",
            "championship",
            "fa cup",
            "league cup"
        ],
        "germany": [
            "bundesliga",
            "2. bundesliga",
            "dfb pokal"
        ],
        "france": [
            "ligue 1",
            "ligue 2",
            "coupe de france"
        ],
        "portugal": [
            "primeira liga",
            "segunda liga",
            "taça de portugal",
            "taca de portugal"
        ],
        "turkey": [
            "süper lig",
            "super lig",
            "1. lig",
            "cup"
        ],
        "argentina": [
            "liga profesional",
            "primera división",
            "primera division",
            "copa argentina",
            "primera nacional"
        ],
        "uruguay": [
            "primera división",
            "primera division"
        ],
        "chile": [
            "primera división",
            "primera division"
        ],
        "colombia": [
            "primera a",
            "copa colombia"
        ],
        "mexico": [
            "liga mx",
            "liga de expansión",
            "liga de expansion"
        ],
        "scotland": [
            "premiership",
            "championship"
        ],
        "netherlands": [
            "eredivisie",
            "eerste divisie"
        ],
        "belgium": [
            "jupiler pro league",
            "challenger pro league"
        ]
    }

    ligas_permitidas = ligas_por_pais.get(pais_n, [])

    for liga_ok in ligas_permitidas:
        if normalizar(liga_ok) in liga_n:
            return True

    return False


# ============================================================
# PRIORIDADES
# ============================================================

def prioridade_canto(time_nome):
    favoritos_altos = [
        "Manchester City",
        "Liverpool",
        "Arsenal",
        "Bayern Munich",
        "Bayern München",
        "Real Madrid",
        "Barcelona",
        "PSG",
        "Paris Saint Germain",
        "Flamengo",
        "Palmeiras",
        "Galatasaray",
        "Fenerbahce",
        "Fenerbahçe",
        "Benfica",
        "Sporting CP",
        "FC Porto",
        "Inter Miami"
    ]

    for favorito in favoritos_altos:
        if eh_time_exato(time_nome, favorito):
            return "🔥"

    if eh_favorito(time_nome):
        return "⚠️"

    return "🧪"


def prioridade_cartao(liga, pais):
    pais_forte = [
        "Brazil",
        "Spain",
        "Italy",
        "Argentina",
        "Turkey",
        "Uruguay",
        "Chile",
        "Colombia"
    ]

    liga_n = normalizar(liga)
    pais_n = normalizar(pais)

    for pais_ok in pais_forte:
        if normalizar(pais_ok) == pais_n:
            return "🔥"

    if "libertadores" in liga_n or "sudamericana" in liga_n:
        return "🔥"

    pais_medio = [
        "England",
        "Germany",
        "France",
        "Portugal",
        "Scotland",
        "Netherlands",
        "Belgium",
        "Mexico"
    ]

    for pais_ok in pais_medio:
        if normalizar(pais_ok) == pais_n:
            return "⚠️"

    return "🧪"


def prioridade_jogador(time_ref):
    times_top = [
        "Manchester City",
        "Bayern Munich",
        "Bayern München",
        "Inter Miami",
        "Liverpool",
        "Manchester United",
        "Flamengo"
    ]

    for time_top in times_top:
        if eh_time_exato(time_ref, time_top):
            return "🔥"

    return "⚠️"


# ============================================================
# API
# ============================================================

def buscar_jogos_hoje():
    hoje = datetime.now().strftime("%Y-%m-%d")

    params = {
        "date": hoje,
        "timezone": "America/Sao_Paulo"
    }

    resposta = requests.get(
        URL_FIXTURES,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    if resposta.status_code != 200:
        print("Erro na API:")
        print(resposta.status_code)
        print(resposta.text)
        return []

    dados = resposta.json()
    return dados.get("response", [])


def nome_time(jogo, lado):
    return jogo["teams"][lado]["name"]


def nome_liga(jogo):
    return jogo["league"]["name"]


def pais_liga(jogo):
    return jogo["league"].get("country", "")


def horario_jogo(jogo):
    data_api = jogo["fixture"]["date"]
    return data_api[11:16]


# ============================================================
# GERAÇÃO DOS CANDIDATOS
# ============================================================

def gerar_candidatos(jogos):
    resultado = {
        "A1 — Cantos 10 min | Mandante forte": [],
        "A2 — Cantos 10 min | Visitante favorito": [],
        "B1 — Cartões 1T | Ambos +0 cartão": [],
        "C1 — Criador + Finalizador": [],
        "C2 — Gol de Cabeça": [],
        "C3 — Gol de Fora da Área": [],
        "D — Builder Favorito": []
    }

    for jogo in jogos:
        casa = nome_time(jogo, "home")
        visitante = nome_time(jogo, "away")
        liga = nome_liga(jogo)
        pais = pais_liga(jogo)
        hora = horario_jogo(jogo)

        # Corta sub, base, reservas e times B/II
        if jogo_bloqueado(casa, visitante, liga):
            continue

        jogo_txt = f"{hora} — {casa} x {visitante}"

        # A1 — Cantos mandante forte
        if eh_favorito(casa):
            emoji = prioridade_canto(casa)

            adicionar_sem_duplicar(
                resultado["A1 — Cantos 10 min | Mandante forte"],
                f"{emoji} {jogo_txt} — olhar {casa} +1 canto em 10 min"
            )

        # A2 — Cantos visitante favorito
        if eh_favorito(visitante):
            emoji = prioridade_canto(visitante)

            adicionar_sem_duplicar(
                resultado["A2 — Cantos 10 min | Visitante favorito"],
                f"{emoji} {jogo_txt} — olhar {visitante} +1 canto em 10 min"
            )

        # B1 — Cartões 1º tempo
        if eh_liga_cartoes(liga, pais):
            emoji = prioridade_cartao(liga, pais)

            adicionar_sem_duplicar(
                resultado["B1 — Cartões 1T | Ambos +0 cartão"],
                f"{emoji} {jogo_txt} — {liga} / {pais} — olhar ambos +0 cartão no 1T"
            )

        # C e D — Jogadores especiais
        for time_ref, sugestoes in TIMES_JOGADORES_ESPECIAIS.items():
            time_no_jogo = (
                eh_time_exato(casa, time_ref)
                or eh_time_exato(visitante, time_ref)
            )

            if not time_no_jogo:
                continue

            emoji_jogador = prioridade_jogador(time_ref)

            for sugestao in sugestoes:
                s = normalizar(sugestao)

                if "cabeca" in s:
                    adicionar_sem_duplicar(
                        resultado["C2 — Gol de Cabeça"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

                elif "fora da area" in s:
                    adicionar_sem_duplicar(
                        resultado["C3 — Gol de Fora da Área"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

                elif "assistencia" in s:
                    adicionar_sem_duplicar(
                        resultado["C1 — Criador + Finalizador"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

            adicionar_sem_duplicar(
                resultado["D — Builder Favorito"],
                f"{emoji_jogador} {jogo_txt} — montar builder: jogador chute/gol + time domínio"
            )

    return resultado


# ============================================================
# ORDENAR E LIMITAR
# ============================================================

def ordenar_por_prioridade(itens):
    def peso(item):
        if item.startswith("🔥"):
            return 1
        if item.startswith("⚠️"):
            return 2
        if item.startswith("🧪"):
            return 3
        return 4

    return sorted(itens, key=peso)


def limitar_lista(dados):
    limites = {
        "A1 — Cantos 10 min | Mandante forte": 6,
        "A2 — Cantos 10 min | Visitante favorito": 6,
        "B1 — Cartões 1T | Ambos +0 cartão": 8,
        "C1 — Criador + Finalizador": 6,
        "C2 — Gol de Cabeça": 6,
        "C3 — Gol de Fora da Área": 6,
        "D — Builder Favorito": 8
    }

    limitado = {}

    for categoria, itens in dados.items():
        itens_ordenados = ordenar_por_prioridade(itens)
        limite = limites.get(categoria, 10)
        limitado[categoria] = itens_ordenados[:limite]

    return limitado


def salvar_jogos_json(dados):
    with open(ARQUIVO_JOGOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    print(f"Arquivo {ARQUIVO_JOGOS} atualizado com sucesso.")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    jogos = buscar_jogos_hoje()

    if not jogos:
        print("Nenhum jogo encontrado.")
    else:
        candidatos = gerar_candidatos(jogos)
        candidatos = limitar_lista(candidatos)
        salvar_jogos_json(candidatos)