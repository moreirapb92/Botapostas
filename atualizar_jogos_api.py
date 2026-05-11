import json
import re
import requests
import unicodedata
import os
from datetime import datetime

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
# TIMES FORTES / OFENSIVOS
# ============================================================

FAVORITOS_CANTOS = [
    "Manchester City", "Manchester United", "Liverpool", "Arsenal",
    "Chelsea", "Tottenham", "Newcastle",

    "Bayern Munich", "Bayern München", "Borussia Dortmund",
    "RB Leipzig", "Bayer Leverkusen", "Hoffenheim", "TSG Hoffenheim",

    "Real Madrid", "Barcelona", "Atletico Madrid", "Atlético Madrid",

    "Paris Saint Germain", "PSG", "Marseille", "Lyon", "Monaco",
    "Lille", "Nice", "Rennes",

    "Benfica", "Sporting CP", "Sporting Lisbon", "FC Porto", "Porto",

    "Ajax", "PSV Eindhoven", "Feyenoord",

    "Club Brugge", "Anderlecht", "Genk", "Union Saint-Gilloise",

    "Galatasaray", "Fenerbahce", "Fenerbahçe", "Besiktas", "Beşiktaş",

    "Juventus", "Inter", "Inter Milan", "Internazionale",
    "AC Milan", "Napoli", "Roma", "Lazio", "Atalanta",

    "Flamengo", "Palmeiras", "Botafogo", "Fluminense",
    "São Paulo", "Sao Paulo", "Corinthians",
    "Atlético Mineiro", "Atletico Mineiro",
    "Cruzeiro", "Grêmio", "Gremio", "Internacional",
    "Athletico Paranaense", "Bragantino", "Fortaleza", "Vasco da Gama",
    "Santos", "Ceará", "Ceara", "Sport Recife", "Sport", "CRB", "Bahia",

    "River Plate", "Boca Juniors", "Independiente", "Racing Club",

    "Inter Miami", "Los Angeles FC", "LAFC", "Columbus Crew", "Cincinnati"
]


RESULTADOS_FAVORITOS = [
    "Arsenal", "Barcelona", "Real Madrid", "Paris Saint Germain", "PSG",
    "FC Porto", "Porto", "Palmeiras", "Flamengo", "Botafogo",
    "Athletico Paranaense", "Bragantino", "São Paulo", "Sao Paulo",
    "Aston Villa", "Como", "Cremonese", "AC Milan", "Lyon", "Lille",
    "Monaco", "Bayern Munich", "Bayern München", "Manchester City",
    "Liverpool", "Benfica", "Sporting CP", "Fenerbahçe", "Fenerbahce",
    "Galatasaray", "Inter Miami", "Cincinnati", "Napoli", "Tottenham",
    "Roma", "Atalanta", "River Plate", "CRB", "Bahia", "Atlético Mineiro",
    "Atletico Mineiro"
]


TIMES_DOMINIO_1T = [
    "Manchester City", "Arsenal", "Liverpool", "Tottenham", "Chelsea",
    "Bayern Munich", "Bayern München", "Borussia Dortmund", "RB Leipzig",
    "Bayer Leverkusen", "TSG Hoffenheim", "Hoffenheim",

    "Real Madrid", "Barcelona", "Atletico Madrid", "Atlético Madrid",

    "PSG", "Paris Saint Germain", "Benfica", "Sporting CP", "FC Porto",
    "Porto", "Ajax", "PSV Eindhoven", "Feyenoord",

    "Napoli", "Roma", "Inter", "AC Milan", "Atalanta", "Lazio",

    "Flamengo", "Palmeiras", "Botafogo", "Atlético Mineiro",
    "Atletico Mineiro", "Cruzeiro", "Bahia", "CRB",

    "River Plate", "Boca Juniors"
]


TIMES_BTTS_VENCER = [
    "Manchester City", "Arsenal", "Liverpool", "Tottenham",
    "Real Madrid", "Barcelona", "PSG", "Paris Saint Germain",
    "Benfica", "Sporting CP", "FC Porto", "Porto",
    "Napoli", "Roma", "Atalanta", "AC Milan",
    "Flamengo", "Palmeiras", "Botafogo", "Atlético Mineiro",
    "Atletico Mineiro", "Bahia", "CRB", "River Plate",
    "New England", "New Mexico United", "Al Ahli Jeddah"
]


# ============================================================
# JOGADORES ESPECIAIS — LUKA
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
        "Carrascal/De La Cruz assistência + Pedro marcar"
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
    ],
    "Benfica": [
        "Pavlidis 1+ chute no alvo + Benfica domínio",
        "Pavlidis cabeça",
        "Di María/Aursnes assistência + Pavlidis marcar"
    ],
    "Sporting CP": [
        "Luis Suárez/Gyökeres 1+ chute no alvo + Sporting domínio",
        "Pedro Gonçalves fora da área",
        "Gonçalo Inácio cabeça"
    ],
    "Napoli": [
        "Højlund/Lukaku 1+ chute no alvo + Napoli domínio",
        "De Bruyne fora da área",
        "Politano fora da área"
    ],
    "Tottenham": [
        "Richarlison 1+ chute no alvo + Tottenham domínio",
        "Richarlison cabeça",
        "Son/Maddison assistência + atacante marcar"
    ],
}


# ============================================================
# TEXTO / NORMALIZAÇÃO
# ============================================================

def normalizar(texto):
    if not texto:
        return ""

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def eh_time_exato(nome_time, referencia):
    return normalizar(nome_time) == normalizar(referencia)


def contem_time(nome_time, lista_times):
    for t in lista_times:
        if eh_time_exato(nome_time, t):
            return True
    return False


def eh_favorito(nome_time):
    return contem_time(nome_time, FAVORITOS_CANTOS)


def eh_favorito_resultado(nome_time):
    return contem_time(nome_time, RESULTADOS_FAVORITOS)


def eh_time_dominio_1t(nome_time):
    return contem_time(nome_time, TIMES_DOMINIO_1T)


def eh_time_btts_vencer(nome_time):
    return contem_time(nome_time, TIMES_BTTS_VENCER)


def adicionar_sem_duplicar(lista, item):
    if item not in lista:
        lista.append(item)


# ============================================================
# BLOQUEIO DE BASE / RESERVAS
# ============================================================

def eh_sub_ou_reserva(nome):
    n = normalizar(nome)

    if re.search(r"\bu(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    if re.search(r"\bsub[- ]?(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    if re.search(r"\bunder[- ]?(15|16|17|18|19|20|21|22|23)\b", n):
        return True

    termos_reserva = [
        "youth", "academy", "reserve", "reserves", "jong "
    ]

    for termo in termos_reserva:
        if termo in n:
            return True

    if re.search(r"\bb\b$", n):
        return True

    if re.search(r"\bii\b$", n):
        return True

    if re.search(r"\biii\b$", n):
        return True

    return False


def jogo_bloqueado(casa, visitante, liga):
    return (
        eh_sub_ou_reserva(casa)
        or eh_sub_ou_reserva(visitante)
        or eh_sub_ou_reserva(liga)
    )


# ============================================================
# FILTROS DE LIGA
# ============================================================

def eh_liga_cartoes(liga, pais):
    liga_n = normalizar(liga)
    pais_n = normalizar(pais)

    termos_feminino = [
        "women", "woman", "feminina", "femenina",
        "feminino", "femenino", "liga f",
        "primera division femenina", "serie a women",
        "super league women"
    ]

    for termo in termos_feminino:
        if termo in liga_n:
            return False

    termos_baixos = [
        "tercera", "quarta", "regional", "state", "district",
        "county", "amateur", "rfef", "provincial",
        "tasmania", "victoria premier league",
        "queensland premier league", "npl"
    ]

    for termo in termos_baixos:
        if termo in liga_n:
            return False

    ligas_especiais = [
        "libertadores", "sudamericana", "copa do brasil",
        "champions league", "europa league", "conference league"
    ]

    for termo in ligas_especiais:
        if termo in liga_n:
            return True

    ligas_por_pais = {
        "brazil": ["serie a", "serie b", "copa do brasil"],
        "spain": ["la liga", "segunda división", "segunda division"],
        "italy": ["serie a", "serie b", "coppa italia"],
        "england": ["premier league", "championship", "fa cup", "league cup"],
        "germany": ["bundesliga", "2. bundesliga", "dfb pokal"],
        "france": ["ligue 1", "ligue 2", "coupe de france"],
        "portugal": ["primeira liga", "segunda liga", "taça de portugal", "taca de portugal"],
        "turkey": ["süper lig", "super lig", "1. lig", "cup"],
        "argentina": ["liga profesional", "primera división", "primera division", "copa argentina", "primera nacional"],
        "uruguay": ["primera división", "primera division"],
        "chile": ["primera división", "primera division"],
        "colombia": ["primera a", "copa colombia"],
        "paraguay": [
            "division profesional", "división profesional",
            "primera división", "primera division",
            "division intermedia", "división intermedia",
            "copa paraguay"
        ],
        "mexico": ["liga mx", "liga de expansión", "liga de expansion"],
        "scotland": ["premiership", "championship"],
        "netherlands": ["eredivisie", "eerste divisie"],
        "belgium": ["jupiler pro league", "challenger pro league"]
    }

    for liga_ok in ligas_por_pais.get(pais_n, []):
        if normalizar(liga_ok) in liga_n:
            return True

    return False


def eh_liga_aberta_gols(liga, pais):
    liga_n = normalizar(liga)
    pais_n = normalizar(pais)

    if any(t in liga_n for t in ["women", "feminina", "femenina", "u19", "u20", "u21", "reserves"]):
        return False

    paises_abertos = [
        "norway", "sweden", "denmark", "netherlands", "belgium",
        "switzerland", "usa", "united states", "saudi-arabia",
        "saudi arabia", "brazil", "mexico", "portugal"
    ]

    ligas_abertas = [
        "mls", "usl", "eliteserien", "obos-ligaen", "allsvenskan",
        "superettan", "1. division", "eredivisie", "eerste divisie",
        "challenge league", "super league", "saudi pro league",
        "serie b", "brasileiro", "primeira liga", "liga mx"
    ]

    if pais_n in paises_abertos:
        return True

    for termo in ligas_abertas:
        if termo in liga_n:
            return True

    return False


def eh_liga_para_dominio_1t(liga, pais):
    liga_n = normalizar(liga)
    pais_n = normalizar(pais)

    if any(t in liga_n for t in ["women", "feminina", "femenina", "u19", "u20", "u21", "reserves"]):
        return False

    paises_ok = [
        "england", "spain", "italy", "germany", "france", "portugal",
        "netherlands", "belgium", "brazil", "argentina", "scotland"
    ]

    ligas_ok = [
        "premier league", "championship", "la liga", "serie a", "serie b",
        "bundesliga", "ligue 1", "primeira liga", "eredivisie",
        "jupiler", "serie a", "serie b", "primera nacional",
        "liga profesional", "copa do brasil"
    ]

    if pais_n in paises_ok:
        return True

    for termo in ligas_ok:
        if termo in liga_n:
            return True

    return False


# ============================================================
# JOGOS QUENTES / EMPATE / CLÁSSICOS
# ============================================================

CLASSICOS = [
    ("Barcelona", "Real Madrid"), ("Real Madrid", "Barcelona"),

    ("Corinthians", "São Paulo"), ("São Paulo", "Corinthians"),
    ("Corinthians", "Sao Paulo"), ("Sao Paulo", "Corinthians"),

    ("Celtic", "Rangers"), ("Rangers", "Celtic"),

    ("AC Milan", "Inter"), ("Inter", "AC Milan"),
    ("Inter Milan", "AC Milan"), ("AC Milan", "Inter Milan"),

    ("Monaco", "Lille"), ("Lille", "Monaco"),

    ("Santos", "Bragantino"), ("Bragantino", "Santos"),

    ("Mirandes", "Eibar"), ("Mirandés", "Eibar"),
    ("Eibar", "Mirandes"), ("Eibar", "Mirandés"),

    ("Grêmio", "Flamengo"), ("Gremio", "Flamengo"),
    ("Flamengo", "Grêmio"), ("Flamengo", "Gremio"),

    ("River Plate", "San Lorenzo"), ("San Lorenzo", "River Plate"),
    ("Bahia", "Cruzeiro"), ("Cruzeiro", "Bahia"),
    ("CRB", "Operário PR"), ("Operário PR", "CRB"),
]


def eh_classico_ou_quente(casa, visitante):
    for a, b in CLASSICOS:
        if eh_time_exato(casa, a) and eh_time_exato(visitante, b):
            return True
    return False


def eh_jogo_equilibrado(casa, visitante):
    if eh_classico_ou_quente(casa, visitante):
        return True

    if eh_favorito(casa) and eh_favorito(visitante):
        return True

    return False


# ============================================================
# PRIORIDADES
# ============================================================

def prioridade_canto(time_nome):
    favoritos_altos = [
        "Manchester City", "Liverpool", "Arsenal", "Bayern Munich",
        "Bayern München", "Real Madrid", "Barcelona", "PSG",
        "Paris Saint Germain", "Flamengo", "Palmeiras",
        "Galatasaray", "Fenerbahce", "Fenerbahçe",
        "Benfica", "Sporting CP", "FC Porto", "Inter Miami"
    ]

    if contem_time(time_nome, favoritos_altos):
        return "🔥"

    if eh_favorito(time_nome):
        return "⚠️"

    return "🧪"


def prioridade_cartao(liga, pais):
    pais_forte = [
        "Brazil", "Spain", "Italy", "Argentina",
        "Turkey", "Uruguay", "Chile", "Colombia",
        "Paraguay"
    ]

    pais_n = normalizar(pais)
    liga_n = normalizar(liga)

    for p in pais_forte:
        if normalizar(p) == pais_n:
            return "🔥"

    if "libertadores" in liga_n or "sudamericana" in liga_n:
        return "🔥"

    return "⚠️"


def prioridade_jogador(time_ref):
    times_top = [
        "Manchester City", "Bayern Munich", "Bayern München",
        "Inter Miami", "Liverpool", "Manchester United",
        "Flamengo", "Arsenal", "Barcelona", "Real Madrid",
        "Paris Saint Germain", "PSG", "FC Porto", "Palmeiras",
        "Benfica", "Sporting CP", "Napoli", "Tottenham"
    ]

    if contem_time(time_ref, times_top):
        return "🔥"

    return "⚠️"


def prioridade_resultado(time_nome):
    times_top = [
        "Arsenal", "Barcelona", "Real Madrid", "Paris Saint Germain",
        "PSG", "FC Porto", "Palmeiras", "Flamengo", "Bayern Munich",
        "Bayern München", "Manchester City", "Liverpool", "Benfica",
        "Sporting CP"
    ]

    if contem_time(time_nome, times_top):
        return "🔥"

    if eh_favorito_resultado(time_nome):
        return "⚠️"

    return "🧪"


def prioridade_dominio_1t(time_nome, liga, pais):
    times_top = [
        "Manchester City", "Arsenal", "Liverpool", "Real Madrid", "Barcelona",
        "PSG", "Paris Saint Germain", "Bayern Munich", "Bayern München",
        "Benfica", "Sporting CP", "FC Porto", "River Plate", "Flamengo"
    ]

    if contem_time(time_nome, times_top):
        return "🔥"

    if eh_time_dominio_1t(time_nome):
        return "⚠️"

    return "🧪"


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
# LINHAS SUGERIDAS FAIXA VIP
# ============================================================

def linhas_dominio_1t(time_forte, adversario):
    if contem_time(time_forte, [
        "Manchester City", "PSG", "Paris Saint Germain", "Arsenal",
        "Liverpool", "Real Madrid", "Barcelona", "Bayern Munich",
        "Bayern München", "Benfica", "Sporting CP", "FC Porto"
    ]):
        return (
            f"{time_forte} +7.5/+8.5 chutes 1T; "
            f"{adversario} -5.5/-6.5 chutes 1T; "
            f"{time_forte} +3/+4 escanteios 1T; "
            f"{adversario} -2/-3 escanteios 1T"
        )

    return (
        f"{time_forte} +5.5/+6.5 chutes 1T; "
        f"{adversario} -6.5/-7.5 chutes 1T; "
        f"{time_forte} +2/+3 escanteios 1T; "
        f"{adversario} -2/-3 escanteios 1T"
    )


def linha_chutes_gol_1t(time_forte, adversario):
    return (
        f"{time_forte} +2.5 chutes ao gol 1T "
        f"ou {adversario} -1.5 chutes ao gol 1T"
    )


# ============================================================
# GERAÇÃO DOS CANDIDATOS
# ============================================================

def gerar_candidatos(jogos):
    resultado = {
        # LUKA
        "[LUKA] A1 — Cantos 10 min | Mandante forte": [],
        "[LUKA] A2 — Cantos 10 min | Visitante favorito": [],

        "[LUKA] B1 — Cartões 1T | Ambos +0 cartão": [],
        "[LUKA] B4 — Cartões FT por time | +2/+3 cartões": [],
        "[LUKA] B5 — Cartões individuais | Clássico/jogo quente": [],

        "[LUKA] C1 — Criador + Finalizador": [],
        "[LUKA] C2 — Gol de Cabeça | Jogos para procurar": [],
        "[LUKA] C3 — Gol de Fora da Área | Jogos para procurar": [],
        "[LUKA] C4 — Roteiro de jogadores | Assistência + gol": [],

        "[LUKA] D — Builder Favorito | Chute no alvo + domínio": [],

        "[LUKA] E1 — Resultado Final | Favoritos para vencer": [],
        "[LUKA] E2 — Resultado Final | Empate candidato": [],

        # FAIXA VIP
        "[FAIXA VIP] H1 — Domínio estatístico 1T | Chutes + escanteios": [],
        "[FAIXA VIP] H2 — Domínio 1T agressivo | Inclui chutes ao gol": [],
        "[FAIXA VIP] H3 — Domínio 1T invertido | Visitante/zebra pressionando": [],
        "[FAIXA VIP] G7 — Resultado final + ambos marcam": [],
        "[FAIXA VIP] C7 — Chutes de jogadores | Procurar linhas": []
    }

    for jogo in jogos:
        casa = nome_time(jogo, "home")
        visitante = nome_time(jogo, "away")
        liga = nome_liga(jogo)
        pais = pais_liga(jogo)
        hora = horario_jogo(jogo)

        if jogo_bloqueado(casa, visitante, liga):
            continue

        jogo_txt = f"{hora} — {casa} x {visitante}"

        # ====================================================
        # LUKA A — CANTOS 10 MIN
        # ====================================================

        if eh_favorito(casa):
            emoji = prioridade_canto(casa)
            adicionar_sem_duplicar(
                resultado["[LUKA] A1 — Cantos 10 min | Mandante forte"],
                f"{emoji} {jogo_txt} — olhar {casa} +1 canto em 10 min"
            )

        if eh_favorito(visitante):
            emoji = prioridade_canto(visitante)
            adicionar_sem_duplicar(
                resultado["[LUKA] A2 — Cantos 10 min | Visitante favorito"],
                f"{emoji} {jogo_txt} — olhar {visitante} +1 canto em 10 min"
            )

        # ====================================================
        # LUKA B — CARTÕES
        # ====================================================

        if eh_liga_cartoes(liga, pais):
            emoji = prioridade_cartao(liga, pais)

            adicionar_sem_duplicar(
                resultado["[LUKA] B1 — Cartões 1T | Ambos +0 cartão"],
                f"{emoji} {jogo_txt} — {liga} / {pais} — olhar ambos +0 cartão no 1T"
            )

            if eh_classico_ou_quente(casa, visitante) or normalizar(pais) in [
                "brazil", "spain", "italy", "argentina", "uruguay",
                "paraguay", "turkey", "scotland", "france"
            ]:
                linha = "+2 cartões FT"
                if eh_classico_ou_quente(casa, visitante):
                    linha = "+2 ou +3 cartões FT"

                adicionar_sem_duplicar(
                    resultado["[LUKA] B4 — Cartões FT por time | +2/+3 cartões"],
                    f"{emoji} {jogo_txt} — olhar {casa} {linha} + {visitante} {linha}"
                )

            if eh_classico_ou_quente(casa, visitante):
                adicionar_sem_duplicar(
                    resultado["[LUKA] B5 — Cartões individuais | Clássico/jogo quente"],
                    f"🔥 {jogo_txt} — olhar 3-4 jogadores para cartão individual"
                )

        # ====================================================
        # LUKA C — JOGADORES ESPECIAIS CADASTRADOS
        # ====================================================

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
                        resultado["[LUKA] C2 — Gol de Cabeça | Jogos para procurar"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

                elif "fora da area" in s:
                    adicionar_sem_duplicar(
                        resultado["[LUKA] C3 — Gol de Fora da Área | Jogos para procurar"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

                elif "assistencia" in s and "marcar" in s:
                    adicionar_sem_duplicar(
                        resultado["[LUKA] C1 — Criador + Finalizador"],
                        f"{emoji_jogador} {jogo_txt} — olhar {sugestao}"
                    )

        # ====================================================
        # LUKA C2 / C3 — CABEÇA E FORA DA ÁREA POR PERFIL
        # ====================================================

        times_no_jogo = []

        if eh_favorito(casa):
            times_no_jogo.append(casa)

        if eh_favorito(visitante):
            times_no_jogo.append(visitante)

        for time_forte in times_no_jogo:
            emoji = prioridade_jogador(time_forte)

            adicionar_sem_duplicar(
                resultado["[LUKA] C2 — Gol de Cabeça | Jogos para procurar"],
                f"{emoji} {jogo_txt} — procurar cabeceio: centroavante/zagueiro do {time_forte}"
            )

            adicionar_sem_duplicar(
                resultado["[LUKA] C3 — Gol de Fora da Área | Jogos para procurar"],
                f"{emoji} {jogo_txt} — procurar fora da área: meia/chutador do {time_forte}"
            )

        # ====================================================
        # LUKA C4 — ROTEIRO ASSISTÊNCIA + GOL
        # ====================================================

        if times_no_jogo:
            for time_forte in times_no_jogo:
                adversario = visitante if eh_time_exato(time_forte, casa) else casa
                emoji = prioridade_jogador(time_forte)

                adicionar_sem_duplicar(
                    resultado["[LUKA] C4 — Roteiro de jogadores | Assistência + gol"],
                    f"{emoji} {jogo_txt} — procurar {time_forte}: criador assistência + atacante marcar; se jogo aberto, procurar também {adversario}: criador assistência + atacante marcar"
                )

        # ====================================================
        # LUKA D — BUILDER FAVORITO
        # ====================================================

        for time_forte in times_no_jogo:
            emoji = prioridade_jogador(time_forte)

            detalhe = "montar builder: jogador 1+ chute no alvo + time mais chutes/chutes ao gol/escanteios"
            if eh_jogo_equilibrado(casa, visitante):
                detalhe = "builder leve: jogador 1+ chute no alvo + domínio, evitar exagerar porque é clássico/equilibrado"

            adicionar_sem_duplicar(
                resultado["[LUKA] D — Builder Favorito | Chute no alvo + domínio"],
                f"{emoji} {jogo_txt} — {time_forte}: {detalhe}"
            )

        # ====================================================
        # LUKA E1 — RESULTADO FINAL FAVORITO
        # ====================================================

        if eh_favorito_resultado(casa) and not eh_jogo_equilibrado(casa, visitante):
            emoji = prioridade_resultado(casa)
            adicionar_sem_duplicar(
                resultado["[LUKA] E1 — Resultado Final | Favoritos para vencer"],
                f"{emoji} {jogo_txt} — olhar {casa} vencer / pagamento antecipado"
            )

        if eh_favorito_resultado(visitante) and not eh_jogo_equilibrado(casa, visitante):
            emoji = prioridade_resultado(visitante)
            adicionar_sem_duplicar(
                resultado["[LUKA] E1 — Resultado Final | Favoritos para vencer"],
                f"{emoji} {jogo_txt} — olhar {visitante} vencer / pagamento antecipado"
            )

        # ====================================================
        # LUKA E2 — EMPATE CANDIDATO
        # ====================================================

        if eh_jogo_equilibrado(casa, visitante):
            adicionar_sem_duplicar(
                resultado["[LUKA] E2 — Resultado Final | Empate candidato"],
                f"⚠️ {jogo_txt} — olhar empate seco se odd 3.00+"
            )

        # ====================================================
        # FAIXA VIP H — DOMÍNIO ESTATÍSTICO 1T
        # ====================================================

        if eh_liga_para_dominio_1t(liga, pais):
            # Mandante dominante
            if eh_time_dominio_1t(casa):
                emoji = prioridade_dominio_1t(casa, liga, pais)
                linhas = linhas_dominio_1t(casa, visitante)

                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] H1 — Domínio estatístico 1T | Chutes + escanteios"],
                    f"{emoji} {jogo_txt} — olhar {linhas}"
                )

                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] H2 — Domínio 1T agressivo | Inclui chutes ao gol"],
                    f"{emoji} {jogo_txt} — H1 + olhar {linha_chutes_gol_1t(casa, visitante)}"
                )

            # Visitante dominante
            if eh_time_dominio_1t(visitante):
                emoji = prioridade_dominio_1t(visitante, liga, pais)
                linhas = linhas_dominio_1t(visitante, casa)

                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] H1 — Domínio estatístico 1T | Chutes + escanteios"],
                    f"{emoji} {jogo_txt} — olhar {linhas}"
                )

                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] H2 — Domínio 1T agressivo | Inclui chutes ao gol"],
                    f"{emoji} {jogo_txt} — H1 + olhar {linha_chutes_gol_1t(visitante, casa)}"
                )

                if not eh_favorito_resultado(visitante) or eh_jogo_equilibrado(casa, visitante):
                    adicionar_sem_duplicar(
                        resultado["[FAIXA VIP] H3 — Domínio 1T invertido | Visitante/zebra pressionando"],
                        f"⚠️ {jogo_txt} — visitante pode dominar 1T: {linhas}"
                    )

            # Jogo equilibrado com possibilidade de mercado invertido
            if eh_jogo_equilibrado(casa, visitante):
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] H3 — Domínio 1T invertido | Visitante/zebra pressionando"],
                    f"🧪 {jogo_txt} — conferir se a bet oferece domínio 1T do lado com linhas menores; buscar over chutes/escanteios do time que começa melhor"
                )

        # ====================================================
        # FAIXA VIP G7 — RESULTADO + AMBOS MARCAM
        # ====================================================

        if eh_liga_aberta_gols(liga, pais) or eh_time_btts_vencer(casa) or eh_time_btts_vencer(visitante):
            if eh_time_btts_vencer(casa) or eh_favorito_resultado(casa):
                emoji = "🔥" if eh_time_btts_vencer(casa) else "⚠️"
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] G7 — Resultado final + ambos marcam"],
                    f"{emoji} {jogo_txt} — olhar {casa} vencer + ambos marcam"
                )

            if eh_time_btts_vencer(visitante) or eh_favorito_resultado(visitante):
                emoji = "🔥" if eh_time_btts_vencer(visitante) else "⚠️"
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] G7 — Resultado final + ambos marcam"],
                    f"{emoji} {jogo_txt} — olhar {visitante} vencer + ambos marcam"
                )

            # Em ligas abertas, mandar opção de zebra/mandante com stake menor
            if eh_liga_aberta_gols(liga, pais) and not eh_favorito_resultado(casa) and not eh_favorito_resultado(visitante):
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] G7 — Resultado final + ambos marcam"],
                    f"🧪 {jogo_txt} — liga aberta: olhar mandante ou zebra vencer + ambos marcam se odd 4.00+"
                )

        # ====================================================
        # FAIXA VIP C7 — CHUTES DE JOGADORES
        # ====================================================

        for time_forte in times_no_jogo:
            emoji = "⚠️"
            adicionar_sem_duplicar(
                resultado["[FAIXA VIP] C7 — Chutes de jogadores | Procurar linhas"],
                f"{emoji} {jogo_txt} — procurar 2-3 jogadores do {time_forte} com +1.5/+2.5 chutes; priorizar atacantes, pontas, meia finalizador e batedor de falta"
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
        # LUKA
        "[LUKA] A1 — Cantos 10 min | Mandante forte": 5,
        "[LUKA] A2 — Cantos 10 min | Visitante favorito": 5,

        "[LUKA] B1 — Cartões 1T | Ambos +0 cartão": 18,
        "[LUKA] B4 — Cartões FT por time | +2/+3 cartões": 14,
        "[LUKA] B5 — Cartões individuais | Clássico/jogo quente": 8,

        "[LUKA] C1 — Criador + Finalizador": 6,
        "[LUKA] C2 — Gol de Cabeça | Jogos para procurar": 8,
        "[LUKA] C3 — Gol de Fora da Área | Jogos para procurar": 8,
        "[LUKA] C4 — Roteiro de jogadores | Assistência + gol": 6,

        "[LUKA] D — Builder Favorito | Chute no alvo + domínio": 10,

        "[LUKA] E1 — Resultado Final | Favoritos para vencer": 8,
        "[LUKA] E2 — Resultado Final | Empate candidato": 6,

        # FAIXA VIP
        "[FAIXA VIP] H1 — Domínio estatístico 1T | Chutes + escanteios": 10,
        "[FAIXA VIP] H2 — Domínio 1T agressivo | Inclui chutes ao gol": 8,
        "[FAIXA VIP] H3 — Domínio 1T invertido | Visitante/zebra pressionando": 6,
        "[FAIXA VIP] G7 — Resultado final + ambos marcam": 10,
        "[FAIXA VIP] C7 — Chutes de jogadores | Procurar linhas": 8
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
