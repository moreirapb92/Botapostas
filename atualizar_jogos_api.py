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
URL_ODDS = "https://v3.football.api-sports.io/odds"
URL_FIXTURE_STATS = "https://v3.football.api-sports.io/fixtures/statistics"
URL_FIXTURE_PLAYERS = "https://v3.football.api-sports.io/fixtures/players"
URL_SQUADS = "https://v3.football.api-sports.io/players/squads"

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
    # Elite Europa
    "Manchester City", "Arsenal", "Liverpool", "Tottenham", "Chelsea",
    "Bayern Munich", "Bayern München", "Borussia Dortmund", "RB Leipzig",
    "Bayer Leverkusen", "TSG Hoffenheim", "Hoffenheim",

    "Real Madrid", "Barcelona", "Atletico Madrid", "Atlético Madrid",

    "PSG", "Paris Saint Germain", "Benfica", "Sporting CP", "FC Porto",
    "Porto", "Ajax", "PSV Eindhoven", "Feyenoord",

    "Napoli", "Roma", "Inter", "AC Milan", "Atalanta", "Lazio",
    "Bologna", "Rayo Vallecano", "Millwall",

    # Brasil / América do Sul
    "Flamengo", "Palmeiras", "Botafogo", "Atlético Mineiro",
    "Atletico Mineiro", "Cruzeiro", "Bahia", "CRB",

    "River Plate", "Boca Juniors", "Independiente", "Racing Club"
]




TIMES_DOMINIO_1T_AGRESSIVO = [
    # Modelo print forte: linhas altas, 5 pernas
    "Manchester City", "Arsenal", "Liverpool", "Tottenham",
    "Real Madrid", "Barcelona", "PSG", "Paris Saint Germain",
    "Bayern Munich", "Bayern München", "Benfica", "Sporting CP",
    "FC Porto", "Porto", "TSG Hoffenheim", "Hoffenheim",

    # Times que apareceram ou combinam com o padrão Faixa VIP
    "Napoli", "Roma", "Atalanta", "Bologna", "Rayo Vallecano",
    "Millwall", "River Plate", "Flamengo", "CRB", "Bahia", "Cruzeiro"
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
# FAIXA VIP / LUKA — ASSISTÊNCIAS
# ============================================================
# Lista manual para ajudar o robô a lembrar quem costuma gerar assistência.
# Sempre conferir titularidade no app antes de apostar.
# Prioridade para: batedor de escanteio, batedor de falta, lateral ofensivo,
# lateral com lateral longo, camisa 10, ponta que cruza muito.

JOGADORES_ASSISTENCIA = {
    "Arsenal": ["Saka", "Odegaard", "Rice", "Martinelli/Trossard"],
    "Manchester City": ["Foden", "Doku", "Bernardo Silva", "Savinho/Cherki"],
    "Liverpool": ["Alexander-Arnold", "Robertson", "Salah", "Szoboszlai"],
    "Tottenham": ["Maddison", "Son", "Kulusevski", "Pedro Porro"],
    "Chelsea": ["Palmer", "Enzo Fernandez", "Reece James", "Cucurella"],

    "Real Madrid": ["Vinicius Jr", "Bellingham", "Rodrygo", "Valverde"],
    "Barcelona": ["Yamal", "Pedri", "Raphinha", "Balde"],
    "Atletico Madrid": ["Griezmann", "Koke", "De Paul", "Llorente"],
    "Atlético Madrid": ["Griezmann", "Koke", "De Paul", "Llorente"],

    "PSG": ["Dembele", "Vitinha", "Hakimi", "Barcola"],
    "Paris Saint Germain": ["Dembele", "Vitinha", "Hakimi", "Barcola"],

    "Benfica": ["Di Maria", "Aursnes", "Kokcu", "Carreras"],
    "Sporting CP": ["Pedro Goncalves", "Trincao", "Nuno Santos/Quenda", "Hjulmand"],
    "FC Porto": ["Pepe", "Galeno", "Francisco Conceicao", "Alan Varela"],
    "Porto": ["Pepe", "Galeno", "Francisco Conceicao", "Alan Varela"],

    "Napoli": ["De Bruyne", "Politano", "Kvaratskhelia/Neres", "Di Lorenzo"],
    "Roma": ["Dybala", "Pellegrini", "Angelino", "Soulé"],
    "AC Milan": ["Pulisic", "Leao", "Theo Hernandez", "Reijnders"],
    "Atalanta": ["Lookman", "De Ketelaere", "Zappacosta", "Koopmeiners"],

    "Flamengo": ["Arrascaeta", "De La Cruz", "Luiz Araujo", "Gerson"],
    "Palmeiras": ["Raphael Veiga", "Estevao", "Piquerez", "Mayke"],
    "Botafogo": ["Savarino", "Almada", "Marlon Freitas", "Cuiabano"],
    "Fluminense": ["Ganso", "Jhon Arias", "Samuel Xavier", "Keno"],
    "Cruzeiro": ["Matheus Pereira", "William", "Keny Arroyo", "Lucas Silva"],
    "Atlético Mineiro": ["Hulk", "Gustavo Scarpa", "Arana", "Bernard"],
    "Atletico Mineiro": ["Hulk", "Gustavo Scarpa", "Arana", "Bernard"],
    "São Paulo": ["Lucas Moura", "Wellington Rato", "Ferreira", "Igor Vinicius"],
    "Sao Paulo": ["Lucas Moura", "Wellington Rato", "Ferreira", "Igor Vinicius"],

    "River Plate": ["Nacho Fernandez", "Quintero", "Acuna", "Meza"],
    "Boca Juniors": ["Zenon", "Paredes", "Advincula", "Blanco"]
}


def sugestao_assistencia_time(time):
    jogadores = None

    for nome, lista in JOGADORES_ASSISTENCIA.items():
        if eh_time_exato(time, nome):
            jogadores = lista
            break

    if jogadores:
        return (
            f"procurar assistência de: {', '.join(jogadores)}; "
            "priorizar quem bater escanteio/falta/lateral e confirmar titularidade"
        )

    return (
        "procurar jogador para assistência: batedor de escanteio, batedor de falta, "
        "lateral ofensivo/lateral longo, camisa 10, ponta que cruza muito; confirmar titularidade"
    )


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
# LUKA C9 — ELENCOS ATUALIZADOS + GOLS/ASSISTÊNCIAS
# ============================================================
# Objetivo: parar de mandar jogador antigo. O bot pega o ID real
# do time no fixture do dia, busca o elenco atual em /players/squads
# e só sugere nomes que aparecem no elenco. Se a API não devolver
# elenco, a sugestão vem marcada como "conferir no app".

TIMES_PRIORITARIOS_C9 = [
    # Inglaterra
    "Liverpool", "Manchester City", "Arsenal", "Chelsea",
    "Manchester United", "Tottenham", "Aston Villa", "Newcastle",
    "West Ham", "Brighton",

    # Espanha
    "Real Madrid", "Barcelona", "Atletico Madrid", "Atlético Madrid",
    "Villarreal", "Sevilla", "Valencia", "Real Sociedad",
    "Athletic Club", "Girona", "Real Betis",

    # França
    "Paris Saint Germain", "PSG", "Lyon", "Marseille", "Monaco",
    "Lille", "Rennes", "Nice", "Lens",

    # Alemanha
    "Bayern Munich", "Bayern München", "Borussia Dortmund", "BVB",
    "Bayer Leverkusen", "RB Leipzig", "Eintracht Frankfurt",
    "Stuttgart", "Wolfsburg",

    # Itália
    "Inter", "Inter Milan", "Internazionale", "AC Milan", "Juventus",
    "Napoli", "Roma", "Atalanta", "Lazio", "Fiorentina",

    # Portugal / Holanda / Bélgica / Turquia
    "Benfica", "Sporting CP", "Sporting Lisbon", "FC Porto", "Porto", "SC Braga",
    "Ajax", "PSV Eindhoven", "PSV", "Feyenoord", "AZ Alkmaar",
    "Club Brugge", "Anderlecht", "Genk", "Union Saint-Gilloise", "Union St. Gilloise",
    "Galatasaray", "Fenerbahce", "Fenerbahçe", "Besiktas", "Beşiktaş",

    # Brasil
    "Flamengo", "Palmeiras", "Botafogo", "Fluminense", "São Paulo", "Sao Paulo",
    "Corinthians", "Santos", "Grêmio", "Gremio", "Internacional", "Cruzeiro",
    "Atlético Mineiro", "Atletico Mineiro", "Bahia", "Fortaleza", "Vasco DA Gama", "Vasco da Gama",

    # Argentina / América
    "River Plate", "Boca Juniors", "Racing Club", "Independiente", "San Lorenzo",
    "Inter Miami", "Los Angeles FC", "LAFC", "New York Red Bulls", "Orlando City",
    "Columbus Crew", "FC Cincinnati",

    # Arábia / outros
    "Al-Hilal", "Al Hilal", "Al Nassr", "Al-Ittihad", "Al Ittihad", "Al Ahli", "Al Ahli Jeddah"
]

# Perfis manuais: usados como prioridade, mas SEMPRE filtrados pelo elenco atual.
# Se o jogador não estiver no squad da API, ele é cortado automaticamente.
JOGADORES_PERFIL_C9 = {
    "Liverpool": {
        "marcadores": ["Mohamed Salah", "Salah", "Cody Gakpo", "Gakpo", "Diogo Jota", "Jota"],
        "assistencias": ["Dominik Szoboszlai", "Szoboszlai", "Mohamed Salah", "Salah", "Alexis Mac Allister", "Mac Allister", "Andrew Robertson", "Robertson"],
        "cabeca": ["Virgil van Dijk", "Van Dijk", "Ibrahima Konaté", "Konate", "Cody Gakpo", "Gakpo"],
        "fora_area": ["Alexis Mac Allister", "Mac Allister", "Dominik Szoboszlai", "Szoboszlai"]
    },
    "Aston Villa": {
        "marcadores": ["Ollie Watkins", "Watkins"],
        "assistencias": ["Morgan Rogers", "Rogers", "John McGinn", "McGinn", "Youri Tielemans", "Tielemans"],
        "cabeca": ["Ollie Watkins", "Watkins", "Pau Torres"],
        "fora_area": ["Morgan Rogers", "Rogers", "Youri Tielemans", "Tielemans"]
    },
    "Paris Saint Germain": {
        "marcadores": ["Kvaratskhelia", "Khvicha Kvaratskhelia", "Gonçalo Ramos", "Goncalo Ramos", "Barcola", "Dembélé", "Dembele"],
        "assistencias": ["Ousmane Dembélé", "Dembele", "Dembélé", "Vitinha", "Hakimi", "Barcola"],
        "cabeca": ["Gonçalo Ramos", "Goncalo Ramos", "Marquinhos", "Pacho"],
        "fora_area": ["Vitinha", "Dembélé", "Dembele"]
    },
    "PSG": {
        "marcadores": ["Kvaratskhelia", "Khvicha Kvaratskhelia", "Gonçalo Ramos", "Goncalo Ramos", "Barcola", "Dembélé", "Dembele"],
        "assistencias": ["Ousmane Dembélé", "Dembele", "Dembélé", "Vitinha", "Hakimi", "Barcola"],
        "cabeca": ["Gonçalo Ramos", "Goncalo Ramos", "Marquinhos", "Pacho"],
        "fora_area": ["Vitinha", "Dembélé", "Dembele"]
    },
    "Real Madrid": {
        "marcadores": ["Kylian Mbappé", "Mbappe", "Vinicius", "Vinícius", "Rodrygo", "Bellingham"],
        "assistencias": ["Vinicius", "Vinícius", "Rodrygo", "Bellingham", "Valverde", "Arda Güler", "Arda Guler"],
        "cabeca": ["Rüdiger", "Rudiger", "Militão", "Militao", "Bellingham"],
        "fora_area": ["Valverde", "Bellingham", "Rodrygo", "Arda Güler", "Arda Guler"]
    },
    "Barcelona": {
        "marcadores": ["Lewandowski", "Ferran Torres", "Raphinha", "Lamine Yamal", "Yamal"],
        "assistencias": ["Lamine Yamal", "Yamal", "Raphinha", "Pedri", "Balde"],
        "cabeca": ["Lewandowski", "Araujo", "Koundé", "Kounde"],
        "fora_area": ["Raphinha", "Pedri", "Fermín", "Fermin"]
    },
    "Manchester City": {
        "marcadores": ["Erling Haaland", "Haaland", "Foden", "Doku", "Savinho", "Cherki"],
        "assistencias": ["Foden", "Doku", "Bernardo Silva", "Savinho", "Cherki"],
        "cabeca": ["Haaland", "Rúben Dias", "Ruben Dias", "Gvardiol"],
        "fora_area": ["Foden", "Bernardo Silva", "Cherki"]
    },
    "Arsenal": {
        "marcadores": ["Saka", "Martinelli", "Trossard", "Havertz", "Gyökeres", "Gyokeres"],
        "assistencias": ["Saka", "Odegaard", "Ødegaard", "Rice", "Martinelli", "Trossard"],
        "cabeca": ["Gabriel Magalhães", "Gabriel Magalhaes", "Saliba", "Havertz", "Gyökeres", "Gyokeres"],
        "fora_area": ["Rice", "Odegaard", "Ødegaard", "Saka"]
    },
    "Chelsea": {
        "marcadores": ["Palmer", "Nicolas Jackson", "Nkunku", "Pedro Neto"],
        "assistencias": ["Palmer", "Enzo Fernandez", "Reece James", "Pedro Neto"],
        "cabeca": ["Nicolas Jackson", "Disasi", "Colwill"],
        "fora_area": ["Palmer", "Enzo Fernandez"]
    },
    "Bayern Munich": {
        "marcadores": ["Harry Kane", "Kane", "Musiala", "Olise", "Sané", "Sane"],
        "assistencias": ["Olise", "Musiala", "Kimmich", "Gnabry", "Sané", "Sane"],
        "cabeca": ["Kane", "Kim Min-Jae", "Upamecano"],
        "fora_area": ["Olise", "Musiala", "Kimmich"]
    },
    "Borussia Dortmund": {
        "marcadores": ["Guirassy", "Adeyemi", "Brandt", "Malen"],
        "assistencias": ["Brandt", "Adeyemi", "Ryerson", "Gross", "Groß"],
        "cabeca": ["Guirassy", "Schlotterbeck", "Süle", "Sule"],
        "fora_area": ["Brandt", "Adeyemi", "Gross", "Groß"]
    },
    "BVB": {
        "marcadores": ["Guirassy", "Adeyemi", "Brandt", "Malen"],
        "assistencias": ["Brandt", "Adeyemi", "Ryerson", "Gross", "Groß"],
        "cabeca": ["Guirassy", "Schlotterbeck", "Süle", "Sule"],
        "fora_area": ["Brandt", "Adeyemi", "Gross", "Groß"]
    },
    "Flamengo": {
        "marcadores": ["Pedro", "Bruno Henrique", "Arrascaeta", "Luiz Araújo", "Luiz Araujo"],
        "assistencias": ["Arrascaeta", "De La Cruz", "Carrascal", "Luiz Araújo", "Luiz Araujo", "Gerson"],
        "cabeca": ["Pedro", "Bruno Henrique", "Léo Pereira", "Leo Pereira"],
        "fora_area": ["Arrascaeta", "De La Cruz", "Gerson", "Carrascal"]
    },
    "Palmeiras": {
        "marcadores": ["Vitor Roque", "Flaco López", "Flaco Lopez", "Estevão", "Estevao", "Raphael Veiga"],
        "assistencias": ["Raphael Veiga", "Estevão", "Estevao", "Piquerez", "Mayke"],
        "cabeca": ["Gustavo Gómez", "Gustavo Gomez", "Murilo", "Flaco López", "Flaco Lopez"],
        "fora_area": ["Raphael Veiga", "Estevão", "Estevao"]
    },
    "Botafogo": {
        "marcadores": ["Igor Jesus", "Savarino", "Almada", "Tiquinho"],
        "assistencias": ["Savarino", "Almada", "Marlon Freitas", "Cuiabano"],
        "cabeca": ["Igor Jesus", "Bastos", "Alexander Barboza"],
        "fora_area": ["Almada", "Savarino", "Marlon Freitas"]
    },
    "Inter Miami": {
        "marcadores": ["Messi", "Luis Suárez", "Luis Suarez", "Suárez", "Suarez", "Berterame"],
        "assistencias": ["Messi", "Jordi Alba", "Alba", "Busquets"],
        "cabeca": ["Luis Suárez", "Luis Suarez", "Berterame"],
        "fora_area": ["Messi"]
    }
}

SQUAD_CACHE = {}


AMBIGUOS_C9 = {
    "inter", "united", "international",
    "arsenal", "barcelona", "liverpool", "newcastle",
    "sporting", "racing", "santos"
}

# Times com nome muito reaproveitado no mundo.
# Para esses, só aceita nome exato ou alias explícito.
# Evita:
# - Arsenal Tula / Arsenal Tivat / Arsenal Sarandi => Arsenal Inglaterra
# - Barcelona SC => Barcelona Espanha
# - Liverpool Montevideo => Liverpool Inglaterra
# - Newcastle Jets => Newcastle United
ALIASES_EXATOS_C9 = {
    "arsenal": {"arsenal", "arsenal fc"},
    "barcelona": {"barcelona", "fc barcelona"},
    "liverpool": {"liverpool", "liverpool fc"},
    "newcastle": {"newcastle united", "newcastle"},
    "inter": {"inter", "inter milan", "internazionale"},
    "internacional": {"internacional", "sc internacional"},
    "santos": {"santos", "santos fc"},
    "racing club": {"racing club"},
    "sporting cp": {"sporting cp", "sporting lisbon"},
    "sporting lisbon": {"sporting cp", "sporting lisbon"},
    "psg": {"psg", "paris saint germain"},
    "paris saint germain": {"psg", "paris saint germain"},
    "bayern munich": {"bayern munich", "bayern münchen", "bayern munchen"},
    "bayern münchen": {"bayern munich", "bayern münchen", "bayern munchen"},
    "borussia dortmund": {"borussia dortmund", "bvb"},
    "bvb": {"borussia dortmund", "bvb"},
    "manchester city": {"manchester city", "man city"},
    "manchester united": {"manchester united", "man united"},
    "fc porto": {"fc porto", "porto"},
    "porto": {"fc porto", "porto"}
}


def match_time_c9(nome_time, referencia):
    """
    Match seguro para C9.
    Regra:
    - nomes famosos/reaproveitados: só exact alias
    - outros nomes: exact ou substring por palavra inteira quando o ref é específico
    """
    nome = normalizar(nome_time)
    ref = normalizar(referencia)

    if not nome or not ref:
        return False

    if nome == ref:
        return True

    if ref in ALIASES_EXATOS_C9:
        return nome in ALIASES_EXATOS_C9[ref]

    if ref in AMBIGUOS_C9 or nome in AMBIGUOS_C9:
        return False

    # Para nomes curtos ou genéricos, não usar substring.
    if len(ref) < 6:
        return False

    # Permite apenas referências específicas.
    # Ex.: "Club Brugge" dentro de "Club Brugge KV".
    if re.search(rf"\b{re.escape(ref)}\b", nome):
        return True

    return False


def eh_time_prioritario_c9(nome_time):
    for referencia in TIMES_PRIORITARIOS_C9:
        if match_time_c9(nome_time, referencia):
            return True
    return False


def buscar_elenco_atual(team_id):
    """Busca elenco atual do time via API-Football /players/squads."""
    if team_id in SQUAD_CACHE:
        return SQUAD_CACHE[team_id]

    try:
        resposta = requests.get(
            URL_SQUADS,
            headers=HEADERS,
            params={"team": team_id},
            timeout=30
        )

        if resposta.status_code != 200:
            SQUAD_CACHE[team_id] = []
            return []

        dados = resposta.json().get("response", [])
        if not dados:
            SQUAD_CACHE[team_id] = []
            return []

        jogadores = []
        for item in dados[0].get("players", []):
            jogadores.append({
                "id": item.get("id"),
                "name": item.get("name", ""),
                "position": item.get("position", "") or "",
                "number": item.get("number")
            })

        SQUAD_CACHE[team_id] = jogadores
        return jogadores

    except Exception as erro:
        print(f"Aviso: erro ao buscar elenco do time {team_id}: {erro}")
        SQUAD_CACHE[team_id] = []
        return []


def buscar_elencos_prioritarios_do_dia(jogos):
    elencos = {}
    for jogo in jogos:
        for lado in ["home", "away"]:
            time = nome_time(jogo, lado)
            if not eh_time_prioritario_c9(time):
                continue
            team_id = id_time(jogo, lado)
            if team_id not in elencos:
                elencos[team_id] = buscar_elenco_atual(team_id)
    return elencos


def mesmo_jogador_c9(a, b):
    """
    Considera apelido/nome completo como o mesmo jogador.
    Ex.: "Watkins" e "Ollie Watkins"; "Salah" e "Mohamed Salah".
    """
    a_n = normalizar(a)
    b_n = normalizar(b)

    if not a_n or not b_n:
        return False

    if a_n == b_n:
        return True

    return (
        re.search(rf"\b{re.escape(a_n)}\b", b_n) is not None
        or re.search(rf"\b{re.escape(b_n)}\b", a_n) is not None
    )


def melhor_nome_c9(a, b):
    """
    Mantém o nome mais completo.
    """
    if not a:
        return b
    if not b:
        return a
    return a if len(a) >= len(b) else b


def deduplicar_nomes_c9(nomes, limite=None):
    saida = []

    for nome in nomes:
        if not nome:
            continue

        nome = str(nome).strip()
        if not nome:
            continue

        substituiu = False
        ja_existe = False

        for i, existente in enumerate(saida):
            if mesmo_jogador_c9(nome, existente):
                melhor = melhor_nome_c9(nome, existente)
                saida[i] = melhor
                substituiu = True
                ja_existe = True
                break

        if not ja_existe and not substituiu:
            saida.append(nome)

        if limite and len(saida) >= limite:
            break

    return saida


def nome_match_elenco_c9(nome, elenco):
    """
    Se o apelido/manual casar com o elenco, retorna o nome oficial do elenco.
    """
    if not nome or not elenco:
        return None

    n = normalizar(nome)

    for jogador in elenco:
        oficial = jogador.get("name", "")
        j = normalizar(oficial)

        if not j:
            continue

        if n == j or re.search(rf"\b{re.escape(n)}\b", j) or re.search(rf"\b{re.escape(j)}\b", n):
            return oficial

    return None


def nome_em_elenco(nome, elenco):
    return nome_match_elenco_c9(nome, elenco) is not None


def nomes_por_posicao(elenco, posicoes, limite=4):
    saida = []
    posicoes_n = [normalizar(p) for p in posicoes]

    for jogador in elenco:
        pos = normalizar(jogador.get("position", ""))

        if any(p in pos for p in posicoes_n):
            nome = jogador.get("name", "")

            if nome:
                saida = deduplicar_nomes_c9(saida + [nome], limite)

        if len(saida) >= limite:
            break

    return saida


def obter_perfil_time_c9(nome_time):
    # Match normal
    for ref, perfil in JOGADORES_PERFIL_C9.items():
        if match_time_c9(nome_time, ref):
            return perfil

    # Aliases manuais para perfis com nomes equivalentes
    aliases_perfil = {
        "bayern münchen": "Bayern Munich",
        "bayern munchen": "Bayern Munich",
        "bvb": "Borussia Dortmund",
        "fc porto": "FC Porto",
        "porto": "FC Porto",
        "psg": "Paris Saint Germain"
    }

    nome = normalizar(nome_time)
    alvo = aliases_perfil.get(nome)

    if alvo and alvo in JOGADORES_PERFIL_C9:
        return JOGADORES_PERFIL_C9[alvo]

    return {}


def filtrar_lista_por_elenco(lista, elenco, limite=4):
    if not lista:
        return []

    lista_limpa = deduplicar_nomes_c9(lista)

    if not elenco:
        # Fallback: API não devolveu elenco; mandar poucos nomes,
        # já sem apelido duplicado, e marcar no texto como conferência obrigatória.
        return deduplicar_nomes_c9(lista_limpa, limite)

    filtrados = []

    for nome in lista_limpa:
        nome_oficial = nome_match_elenco_c9(nome, elenco)

        if nome_oficial:
            filtrados = deduplicar_nomes_c9(filtrados + [nome_oficial], limite)

        if len(filtrados) >= limite:
            break

    return filtrados


def juntar_opcoes(opcoes, limite=3):
    return deduplicar_nomes_c9(opcoes, limite)


def gerar_perfis_c9_time(nome_time, elenco):
    perfil = obter_perfil_time_c9(nome_time)

    marcadores = filtrar_lista_por_elenco(perfil.get("marcadores", []), elenco, 4)
    assistencias = filtrar_lista_por_elenco(perfil.get("assistencias", []), elenco, 4)
    cabeca = filtrar_lista_por_elenco(perfil.get("cabeca", []), elenco, 3)
    fora_area = filtrar_lista_por_elenco(perfil.get("fora_area", []), elenco, 3)

    # Fallback por posição do elenco atual. Evita jogador transferido.
    if elenco:
        marcadores = juntar_opcoes(marcadores + nomes_por_posicao(elenco, ["Attacker", "Forward"], 4), 4)
        assistencias = juntar_opcoes(assistencias + nomes_por_posicao(elenco, ["Midfielder", "Attacker", "Forward"], 4), 4)
        cabeca = juntar_opcoes(cabeca + nomes_por_posicao(elenco, ["Defender", "Attacker", "Forward"], 3), 3)
        fora_area = juntar_opcoes(fora_area + nomes_por_posicao(elenco, ["Midfielder"], 3), 3)

    return {
        "marcadores": marcadores,
        "assistencias": assistencias,
        "cabeca": cabeca,
        "fora_area": fora_area,
        "elenco_confirmado": bool(elenco)
    }


def montar_linhas_c9(jogo_txt, nome_time, perfis, adversario=None):
    marcadores = perfis.get("marcadores", [])
    assistencias = perfis.get("assistencias", [])
    cabeca = perfis.get("cabeca", [])
    fora_area = perfis.get("fora_area", [])
    confirmado = perfis.get("elenco_confirmado", False)
    aviso = "" if confirmado else " ⚠️ confirmar elenco/titularidade no app"

    linhas = []

    if marcadores and assistencias:
        linhas.append({
            "categoria": "[LUKA] C9 — Gols e assistências | elenco atualizado",
            "texto": (
                f"🔥 {jogo_txt} — {nome_time}: C9 pronto{aviso}; "
                f"marcar: {', '.join(marcadores[:3])}; assistência: {', '.join(assistencias[:3])}. "
                f"Montar: assistência + marcador ou 2 marcadores; odd alvo 4.00+"
            )
        })
        linhas.append({
            "categoria": "[LUKA] C4 — Roteiro de jogadores | Assistência + gol",
            "texto": (
                f"🔥 {jogo_txt} — {nome_time}: {assistencias[0]} assistência + "
                f"{marcadores[0]} marcar; alternativa: {assistencias[1] if len(assistencias) > 1 else assistencias[0]} assistência + "
                f"{marcadores[1] if len(marcadores) > 1 else marcadores[0]} marcar"
            )
        })

    marcadores_distintos = deduplicar_nomes_c9(marcadores)
    assistencias_distintas = [
        a for a in deduplicar_nomes_c9(assistencias)
        if not any(mesmo_jogador_c9(a, m) for m in marcadores_distintos[:2])
    ]

    if marcadores_distintos and assistencias_distintas:
        if len(marcadores_distintos) >= 2:
            roteiro = (
                f"{marcadores_distintos[0]} marcar + "
                f"{marcadores_distintos[1]} marcar + "
                f"{assistencias_distintas[0]} assistência"
            )
        elif len(assistencias_distintas) >= 2:
            roteiro = (
                f"{marcadores_distintos[0]} marcar + "
                f"{assistencias_distintas[0]} assistência + "
                f"{assistencias_distintas[1]} assistência"
            )
        else:
            roteiro = ""

        if roteiro:
            linhas.append({
                "categoria": "[LUKA] C9.1 — Odd 20–60 | roteiro agressivo",
                "texto": f"🧪 {jogo_txt} — odd alta controlada: {roteiro}; stake R$0,25/R$0,50"
            })

    if cabeca:
        base_assist = assistencias[0] if assistencias else "batedor de escanteio/falta"
        linhas.append({
            "categoria": "[LUKA] C2 — Gol de Cabeça | Jogos para procurar",
            "texto": f"🔥 {jogo_txt} — {nome_time}: olhar {cabeca[0]} cabeça; combinar {base_assist} assistência + {cabeca[0]} cabeça"
        })

    if fora_area:
        linhas.append({
            "categoria": "[LUKA] C3 — Gol de Fora da Área | Jogos para procurar",
            "texto": f"🧪 {jogo_txt} — {nome_time}: olhar fora da área de {', '.join(fora_area[:2])}"
        })

    return linhas



# ============================================================
# BLOQUEIO DE BASE / RESERVAS / FEMININO
# ============================================================

def eh_feminino(nome):
    n = normalizar(nome)

    termos = [
        " women", "woman", "feminina", "femenina", "feminino", "femenino",
        "frauen", "liga f", "serie a women", "super league women"
    ]

    if any(t in f" {n}" for t in termos):
        return True

    # Muitos jogos femininos aparecem como "Team W" ou "Team (F)".
    if re.search(r"(\s|^)(w|f)$", n):
        return True

    if re.search(r"\((w|f)\)$", n):
        return True

    return False


def eh_sub_ou_reserva(nome):
    n = normalizar(nome)

    if eh_feminino(nome):
        return True

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

    if eh_feminino(liga) or any(t in liga_n for t in ["u19", "u20", "u21", "reserves"]):
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

    if eh_feminino(liga) or any(t in liga_n for t in ["u19", "u20", "u21", "reserves"]):
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


def converter_odd(valor):
    try:
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


def buscar_odds_hoje():
    """
    Busca odds pré-jogo de vencedor da partida.
    Se a API/conta não liberar odds, o robô continua funcionando pelo modo antigo.
    """
    hoje = datetime.now().strftime("%Y-%m-%d")

    odds_por_fixture = {}
    pagina = 1
    total_paginas = 1

    while pagina <= total_paginas and pagina <= 3:
        params = {
            "date": hoje,
            "timezone": "America/Sao_Paulo",
            "bet": 1,
            "page": pagina
        }

        try:
            resposta = requests.get(
                URL_ODDS,
                headers=HEADERS,
                params=params,
                timeout=30
            )
        except Exception as erro:
            print("Aviso: não consegui buscar odds.")
            print(erro)
            return odds_por_fixture

        if resposta.status_code != 200:
            print("Aviso: odds não disponíveis ou erro na API de odds.")
            print(resposta.status_code)
            print(resposta.text)
            return odds_por_fixture

        dados = resposta.json()

        erros = dados.get("errors")
        if erros:
            print("Aviso: API retornou erro nas odds, seguindo sem odds.")
            print(erros)
            return odds_por_fixture

        paging = dados.get("paging", {})
        total_paginas = min(int(paging.get("total", 1) or 1), 3)

        for item in dados.get("response", []):
            fixture = item.get("fixture", {})
            fixture_id = fixture.get("id")

            if not fixture_id:
                continue

            odds_match = extrair_odds_match_winner(item)

            if odds_match:
                odds_por_fixture[fixture_id] = odds_match

        pagina += 1

    print(f"Odds carregadas para {len(odds_por_fixture)} jogos.")
    return odds_por_fixture



# ============================================================
# MÉDIAS DE CHUTES / ESCANTEIOS — PRÉ-JOGO
# ============================================================
# A API geralmente entrega estatísticas por jogo inteiro.
# Para 1º tempo, usamos estimativa: chutes 1T ≈ 47% do jogo,
# escanteios 1T ≈ 45% do jogo.
# Isso não substitui leitura live. Serve para filtrar melhor.

STAT_CACHE_FIXTURE = {}
STAT_CACHE_TEAM = {}


def numero_stat(valor):
    if valor is None:
        return 0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).replace("%", "").replace(",", ".").strip()

    try:
        return float(texto)
    except Exception:
        return 0


def buscar_ultimos_jogos_time(team_id, limite=5):
    chave = (team_id, limite)

    if chave in STAT_CACHE_TEAM:
        return STAT_CACHE_TEAM[chave].get("fixtures", [])

    try:
        resposta = requests.get(
            URL_FIXTURES,
            headers=HEADERS,
            params={
                "team": team_id,
                "last": limite,
                "status": "FT",
                "timezone": "America/Sao_Paulo"
            },
            timeout=30
        )

        if resposta.status_code != 200:
            return []

        jogos = resposta.json().get("response", [])
        STAT_CACHE_TEAM[chave] = {"fixtures": jogos}
        return jogos

    except Exception as erro:
        print(f"Aviso: erro ao buscar últimos jogos do time {team_id}: {erro}")
        return []


def buscar_estatisticas_fixture(fixture_id):
    if fixture_id in STAT_CACHE_FIXTURE:
        return STAT_CACHE_FIXTURE[fixture_id]

    try:
        resposta = requests.get(
            URL_FIXTURE_STATS,
            headers=HEADERS,
            params={"fixture": fixture_id},
            timeout=30
        )

        if resposta.status_code != 200:
            return []

        dados = resposta.json().get("response", [])
        STAT_CACHE_FIXTURE[fixture_id] = dados
        return dados

    except Exception as erro:
        print(f"Aviso: erro ao buscar estatísticas do fixture {fixture_id}: {erro}")
        return []


def extrair_stats_time_fixture(stats_fixture, team_id):
    """
    Retorna stats do time e do adversário dentro do mesmo fixture.
    """
    stats_time = {}
    stats_rival = {}

    for bloco in stats_fixture:
        bloco_team_id = bloco.get("team", {}).get("id")
        destino = stats_time if bloco_team_id == team_id else stats_rival

        for stat in bloco.get("statistics", []):
            tipo = normalizar(stat.get("type", ""))
            valor = numero_stat(stat.get("value"))

            if "total shots" in tipo:
                destino["total_shots"] = valor
            elif "shots on goal" in tipo:
                destino["shots_on_goal"] = valor
            elif "corner kicks" in tipo:
                destino["corners"] = valor
            elif "yellow cards" in tipo:
                destino["yellow_cards"] = valor
            elif "red cards" in tipo:
                destino["red_cards"] = valor

    return stats_time, stats_rival


def media(lista):
    valores = [v for v in lista if v is not None]
    if not valores:
        return 0
    return sum(valores) / len(valores)


def calcular_medias_time(team_id, limite=5):
    """
    Calcula média dos últimos jogos:
    - chutes a favor
    - chutes ao gol a favor
    - escanteios a favor
    - chutes sofridos
    - escanteios sofridos

    Observação: normalmente isso vem por jogo inteiro, não por 1º tempo.
    """
    chave = (team_id, "medias", limite)

    if chave in STAT_CACHE_TEAM:
        return STAT_CACHE_TEAM[chave]

    jogos = buscar_ultimos_jogos_time(team_id, limite)

    chutes_for = []
    sot_for = []
    cantos_for = []
    cards_for = []
    yellow_for = []
    red_for = []

    chutes_against = []
    sot_against = []
    cantos_against = []
    cards_against = []
    yellow_against = []
    red_against = []

    for jogo in jogos:
        fixture_id = jogo.get("fixture", {}).get("id")

        if not fixture_id:
            continue

        stats_fixture = buscar_estatisticas_fixture(fixture_id)

        if not stats_fixture:
            continue

        stats_time, stats_rival = extrair_stats_time_fixture(stats_fixture, team_id)

        y_for = stats_time.get("yellow_cards", 0)
        r_for = stats_time.get("red_cards", 0)
        y_against = stats_rival.get("yellow_cards", 0)
        r_against = stats_rival.get("red_cards", 0)

        chutes_for.append(stats_time.get("total_shots", 0))
        sot_for.append(stats_time.get("shots_on_goal", 0))
        cantos_for.append(stats_time.get("corners", 0))
        yellow_for.append(y_for)
        red_for.append(r_for)
        cards_for.append(y_for + r_for)

        chutes_against.append(stats_rival.get("total_shots", 0))
        sot_against.append(stats_rival.get("shots_on_goal", 0))
        cantos_against.append(stats_rival.get("corners", 0))
        yellow_against.append(y_against)
        red_against.append(r_against)
        cards_against.append(y_against + r_against)

    qtd = len(chutes_for)

    medias = {
        "jogos": qtd,
        "shots_for": media(chutes_for),
        "sot_for": media(sot_for),
        "corners_for": media(cantos_for),
        "cards_for": media(cards_for),
        "yellow_for": media(yellow_for),
        "red_for": media(red_for),

        "shots_against": media(chutes_against),
        "sot_against": media(sot_against),
        "corners_against": media(cantos_against),
        "cards_against": media(cards_against),
        "yellow_against": media(yellow_against),
        "red_against": media(red_against),
    }

    STAT_CACHE_TEAM[chave] = medias
    return medias


def id_time(jogo, lado):
    return jogo["teams"][lado]["id"]


def selecionar_times_para_medias(jogos, odds_por_fixture, max_times=12):
    """
    Evita gastar muitas chamadas na API.
    Só calcula médias dos times mais relevantes:
    favorito por odd, times fortes e jogos bons para H1/H2.
    """
    selecionados = []

    def adicionar(team_id):
        if team_id and team_id not in selecionados:
            selecionados.append(team_id)

    for jogo in jogos:
        casa = nome_time(jogo, "home")
        visitante = nome_time(jogo, "away")
        liga = nome_liga(jogo)
        pais = pais_liga(jogo)

        if not (eh_liga_para_dominio_1t(liga, pais) or eh_liga_cartoes(liga, pais)):
            continue

        favorito_odd = obter_favorito_por_odd(jogo, odds_por_fixture)

        # Para cartões, interessa calcular os dois times.
        if eh_liga_cartoes(liga, pais):
            adicionar(id_time(jogo, "home"))
            adicionar(id_time(jogo, "away"))

        if favorito_odd and favorito_odd["odd"] <= 2.50:
            lado = favorito_odd["lado"]
            adicionar(id_time(jogo, lado))
            adicionar(id_time(jogo, "away" if lado == "home" else "home"))

        elif eh_time_dominio_1t(casa) or eh_favorito(casa):
            adicionar(id_time(jogo, "home"))
            adicionar(id_time(jogo, "away"))

        elif eh_time_dominio_1t(visitante) or eh_favorito(visitante):
            adicionar(id_time(jogo, "away"))
            adicionar(id_time(jogo, "home"))

        if len(selecionados) >= max_times:
            break

    return selecionados[:max_times]


def buscar_medias_times_do_dia(jogos, odds_por_fixture):
    medias = {}

    times = selecionar_times_para_medias(jogos, odds_por_fixture, max_times=18)

    print(f"Calculando médias de chutes/escanteios/cartões para {len(times)} times...")

    for team_id in times:
        medias[team_id] = calcular_medias_time(team_id, limite=5)

    return medias


def obter_medias_jogo(jogo, medias_por_time):
    home_id = id_time(jogo, "home")
    away_id = id_time(jogo, "away")

    return medias_por_time.get(home_id), medias_por_time.get(away_id)


def linha_over_chutes_1t(est):
    if est >= 8.0:
        return "+7.5"
    if est >= 7.0:
        return "+6.5"
    if est >= 6.0:
        return "+5.5"
    if est >= 5.0:
        return "+4.5"
    return "evitar over chutes"


def linha_under_chutes_1t(est):
    if est <= 5.5:
        return "-6.5"
    if est <= 6.5:
        return "-7.5"
    if est <= 7.5:
        return "-8.5"
    if est <= 8.5:
        return "-9.5"
    return "evitar under chutes"


def linha_over_cantos_1t(est):
    if est >= 3.2:
        return "+3"
    if est >= 2.2:
        return "+2"
    if est >= 1.2:
        return "+1"
    return "evitar over cantos"


def linha_under_cantos_1t(est):
    if est <= 1.8:
        return "-2"
    if est <= 2.6:
        return "-3"
    if est <= 3.4:
        return "-4"
    return "evitar under cantos"


def montar_linha_h_stats(time_forte, adversario, stats_forte, stats_adv):
    if not stats_forte or not stats_adv:
        return None

    if stats_forte.get("jogos", 0) < 3 or stats_adv.get("jogos", 0) < 3:
        return None

    # Combina produção do time com o que o adversário costuma ceder.
    exp_chutes_full = (stats_forte["shots_for"] + stats_adv["shots_against"]) / 2
    exp_cantos_full = (stats_forte["corners_for"] + stats_adv["corners_against"]) / 2

    exp_adv_chutes_full = (stats_adv["shots_for"] + stats_forte["shots_against"]) / 2
    exp_adv_cantos_full = (stats_adv["corners_for"] + stats_forte["corners_against"]) / 2

    exp_chutes_1t = exp_chutes_full * 0.47
    exp_cantos_1t = exp_cantos_full * 0.45
    exp_adv_chutes_1t = exp_adv_chutes_full * 0.47
    exp_adv_cantos_1t = exp_adv_cantos_full * 0.45

    over_chutes = linha_over_chutes_1t(exp_chutes_1t)
    over_cantos = linha_over_cantos_1t(exp_cantos_1t)
    under_adv_chutes = linha_under_chutes_1t(exp_adv_chutes_1t)
    under_adv_cantos = linha_under_cantos_1t(exp_adv_cantos_1t)

    score = 0
    if "evitar" not in over_chutes:
        score += 1
    if "evitar" not in over_cantos:
        score += 1
    if "evitar" not in under_adv_chutes:
        score += 1
    if "evitar" not in under_adv_cantos:
        score += 1

    if exp_chutes_1t >= 5.5 and exp_cantos_1t >= 1.6:
        score += 1

    if score < 3:
        return None

    return (
        f"{time_forte}: média {stats_forte['shots_for']:.1f} chutes/jogo, "
        f"{stats_forte['corners_for']:.1f} cantos/jogo; "
        f"estimado 1T: {exp_chutes_1t:.1f} chutes, {exp_cantos_1t:.1f} cantos. "
        f"Olhar {time_forte} {over_chutes} chutes 1T; "
        f"{adversario} {under_adv_chutes} chutes 1T; "
        f"{time_forte} {over_cantos} escanteios 1T; "
        f"{adversario} {under_adv_cantos} escanteios 1T."
    )



def linha_cartao_ft(media_full):
    """
    Linha de cartões no jogo inteiro.
    Bet365 costuma mostrar como +1, +2, +3 cartões por time.
    """
    if media_full >= 2.6:
        return "+2 ou +3 cartões FT"
    if media_full >= 1.7:
        return "+2 cartões FT"
    if media_full >= 1.0:
        return "+1 cartão FT"
    return "evitar cartões FT"


def linha_cartao_2t(media_full):
    """
    Estimativa simples: cartões costumam pesar mais no 2º tempo.
    Usamos 60% da média FT como aproximação para 2T.
    """
    estimado_2t = media_full * 0.60

    if estimado_2t >= 1.45:
        return "+2 cartões no 2T"
    if estimado_2t >= 0.70:
        return "+1 cartão no 2T"
    return "evitar cartão 2T"


def montar_linha_cartoes_stats(casa, visitante, stats_casa, stats_visitante):
    if not stats_casa or not stats_visitante:
        return None

    if stats_casa.get("jogos", 0) < 3 or stats_visitante.get("jogos", 0) < 3:
        return None

    # Esperado do time = disciplina própria + quanto o adversário costuma fazer o rival tomar cartão.
    exp_casa_full = (stats_casa.get("cards_for", 0) + stats_visitante.get("cards_against", 0)) / 2
    exp_visitante_full = (stats_visitante.get("cards_for", 0) + stats_casa.get("cards_against", 0)) / 2

    exp_casa_2t = exp_casa_full * 0.60
    exp_visitante_2t = exp_visitante_full * 0.60

    linha_casa_ft = linha_cartao_ft(exp_casa_full)
    linha_visitante_ft = linha_cartao_ft(exp_visitante_full)
    linha_casa_2t = linha_cartao_2t(exp_casa_full)
    linha_visitante_2t = linha_cartao_2t(exp_visitante_full)

    boas = []
    if "evitar" not in linha_casa_ft or "evitar" not in linha_casa_2t:
        boas.append(casa)
    if "evitar" not in linha_visitante_ft or "evitar" not in linha_visitante_2t:
        boas.append(visitante)

    if not boas:
        return None

    if exp_casa_full < 1.0 and exp_visitante_full < 1.0:
        return None

    texto_base = (
        f"{casa}: média {stats_casa.get('cards_for', 0):.1f} cartões/jogo; "
        f"estimado contra este rival: {exp_casa_full:.1f} FT / {exp_casa_2t:.1f} 2T. "
        f"Olhar {casa} {linha_casa_ft} ou {linha_casa_2t}. "
        f"{visitante}: média {stats_visitante.get('cards_for', 0):.1f} cartões/jogo; "
        f"estimado contra este rival: {exp_visitante_full:.1f} FT / {exp_visitante_2t:.1f} 2T. "
        f"Olhar {visitante} {linha_visitante_ft} ou {linha_visitante_2t}."
    )

    if exp_casa_2t >= 0.70 and exp_visitante_2t >= 0.70:
        texto_base += " Combo possível: ambos +1 cartão no 2T, se a odd compensar."

    if exp_casa_full >= 1.7 and exp_visitante_full >= 1.7:
        texto_base += " Combo possível: ambos +2 cartões FT."

    return texto_base


# ============================================================
# RANKING REAL DE JOGADORES — CHUTES / SOT / GOLS / ASSISTÊNCIAS
# ============================================================
# Usa últimos jogos do time + endpoint /fixtures/players.
# Nem todas as ligas têm cobertura completa. Se não vier dado, o robô
# continua usando a lista manual/perfil.

PLAYER_CACHE_FIXTURE = {}
PLAYER_CACHE_TEAM = {}


def buscar_jogadores_fixture(fixture_id):
    if fixture_id in PLAYER_CACHE_FIXTURE:
        return PLAYER_CACHE_FIXTURE[fixture_id]

    try:
        resposta = requests.get(
            URL_FIXTURE_PLAYERS,
            headers=HEADERS,
            params={"fixture": fixture_id},
            timeout=30
        )

        if resposta.status_code != 200:
            PLAYER_CACHE_FIXTURE[fixture_id] = []
            return []

        dados = resposta.json().get("response", [])
        PLAYER_CACHE_FIXTURE[fixture_id] = dados
        return dados

    except Exception as erro:
        print(f"Aviso: erro ao buscar jogadores do fixture {fixture_id}: {erro}")
        PLAYER_CACHE_FIXTURE[fixture_id] = []
        return []


def jogador_em_lista_assistencia(time_nome, jogador_nome):
    """
    Dá um pequeno boost para jogadores conhecidos por escanteio/falta/lateral.
    A lista manual não substitui os dados reais; só ajuda a ordenar.
    """
    try:
        lista = None

        for time_ref, jogadores in JOGADORES_ASSISTENCIA.items():
            if eh_time_exato(time_nome, time_ref):
                lista = jogadores
                break

        if not lista:
            return False

        jn = normalizar(jogador_nome)

        for nome_manual in lista:
            partes = re.split(r"[/,]", nome_manual)

            for parte in partes:
                parte_n = normalizar(parte).strip()

                if parte_n and (parte_n in jn or jn in parte_n):
                    return True

        return False

    except Exception:
        return False


def calcular_rank_jogadores_time(team_id, team_name="", limite=5):
    """
    Rank dos jogadores pelos últimos jogos:
    - média de chutes
    - média de chutes no alvo
    - gols recentes
    - assistências
    - passes-chave

    Média é por aparição com minutos > 0.
    """
    chave = (team_id, "player_rank", limite)

    if chave in PLAYER_CACHE_TEAM:
        return PLAYER_CACHE_TEAM[chave]

    jogos = buscar_ultimos_jogos_time(team_id, limite)

    jogadores = {}

    for jogo in jogos:
        fixture_id = jogo.get("fixture", {}).get("id")

        if not fixture_id:
            continue

        blocos = buscar_jogadores_fixture(fixture_id)

        if not blocos:
            continue

        for bloco_time in blocos:
            if bloco_time.get("team", {}).get("id") != team_id:
                continue

            for item in bloco_time.get("players", []):
                player = item.get("player", {})
                nome = player.get("name", "Jogador")
                player_id = player.get("id") or nome

                for stats in item.get("statistics", []):
                    games = stats.get("games", {}) or {}
                    shots = stats.get("shots", {}) or {}
                    goals = stats.get("goals", {}) or {}
                    passes = stats.get("passes", {}) or {}

                    minutos = games.get("minutes") or 0

                    # Ignorar quem quase não jogou no jogo.
                    if minutos <= 0:
                        continue

                    if player_id not in jogadores:
                        jogadores[player_id] = {
                            "jogador": nome,
                            "posicao": games.get("position") or "",
                            "aparicoes": 0,
                            "minutos": 0,
                            "chutes": 0,
                            "chutes_no_alvo": 0,
                            "gols": 0,
                            "assistencias": 0,
                            "passes_chave": 0,
                        }

                    d = jogadores[player_id]

                    d["aparicoes"] += 1
                    d["minutos"] += minutos
                    d["chutes"] += shots.get("total") or 0
                    d["chutes_no_alvo"] += shots.get("on") or 0
                    d["gols"] += goals.get("total") or 0
                    d["assistencias"] += goals.get("assists") or 0
                    d["passes_chave"] += passes.get("key") or 0

    ranking = []

    for _, d in jogadores.items():
        apps = max(d["aparicoes"], 1)
        avg_min = d["minutos"] / apps

        # Evitar atletas que entram pouco.
        if avg_min < 25:
            continue

        media_chutes = d["chutes"] / apps
        media_sot = d["chutes_no_alvo"] / apps
        media_gols = d["gols"] / apps
        media_assist = d["assistencias"] / apps
        media_key = d["passes_chave"] / apps

        bola_parada = jogador_em_lista_assistencia(team_name, d["jogador"])

        score_chute = (
            media_chutes * 1.20
            + media_sot * 1.80
            + media_gols * 1.20
            + min(avg_min, 90) / 90
        )

        score_sot = (
            media_sot * 2.50
            + media_chutes * 0.70
            + media_gols * 1.30
            + min(avg_min, 90) / 120
        )

        score_assist = (
            media_key * 1.40
            + media_assist * 3.00
            + (0.80 if bola_parada else 0)
            + min(avg_min, 90) / 180
        )

        ranking.append({
            "jogador": d["jogador"],
            "posicao": d["posicao"],
            "aparicoes": d["aparicoes"],
            "media_minutos": round(avg_min, 1),
            "media_chutes": round(media_chutes, 2),
            "media_sot": round(media_sot, 2),
            "gols": d["gols"],
            "assistencias": d["assistencias"],
            "passes_chave": d["passes_chave"],
            "media_passes_chave": round(media_key, 2),
            "bola_parada": bola_parada,
            "score_chute": round(score_chute, 2),
            "score_sot": round(score_sot, 2),
            "score_assist": round(score_assist, 2),
        })

    PLAYER_CACHE_TEAM[chave] = ranking
    return ranking


def buscar_rank_jogadores_times_do_dia(jogos, odds_por_fixture):
    """
    Calcula ranking de jogadores só para times mais relevantes do dia
    para não gastar chamadas demais na API.
    """
    rankings = {}

    times = selecionar_times_para_medias(jogos, odds_por_fixture, max_times=10)

    print(f"Calculando ranking de jogadores para {len(times)} times...")

    nomes_por_id = {}

    for jogo in jogos:
        for lado in ["home", "away"]:
            nomes_por_id[id_time(jogo, lado)] = nome_time(jogo, lado)

    for team_id in times:
        team_name = nomes_por_id.get(team_id, "")
        rankings[team_id] = calcular_rank_jogadores_time(team_id, team_name, limite=5)

    return rankings


def obter_rank_jogadores_jogo(jogo, rankings_por_time):
    home_id = id_time(jogo, "home")
    away_id = id_time(jogo, "away")

    return rankings_por_time.get(home_id, []), rankings_por_time.get(away_id, [])


def escolher_rank_do_time(time_nome, casa, visitante, rank_home, rank_away):
    if eh_time_exato(time_nome, casa):
        return rank_home

    if eh_time_exato(time_nome, visitante):
        return rank_away

    return []


def linha_jogador_sot(j):
    if j["media_sot"] >= 1.00:
        return "1+ chute no alvo forte"
    if j["media_sot"] >= 0.60:
        return "1+ chute no alvo aceitável"
    if j["media_chutes"] >= 2.20:
        return "1+ chute no alvo possível / melhor +1.5 chutes"
    return "mais indicado para +1.5 chutes"


def formatar_top_sot(ranking, limite=3):
    if not ranking:
        return ""

    candidatos = sorted(
        ranking,
        key=lambda x: x["score_sot"],
        reverse=True
    )[:limite]

    partes = []

    for j in candidatos:
        partes.append(
            f"{j['jogador']} ({j['media_chutes']} ch/j, {j['media_sot']} SOT/j, "
            f"{j['gols']} gols, {linha_jogador_sot(j)})"
        )

    return "; ".join(partes)


def formatar_top_chutes(ranking, limite=3):
    if not ranking:
        return ""

    candidatos = sorted(
        ranking,
        key=lambda x: x["score_chute"],
        reverse=True
    )[:limite]

    partes = []

    for j in candidatos:
        linha = "+2.5 chutes" if j["media_chutes"] >= 2.70 else "+1.5 chutes"

        partes.append(
            f"{j['jogador']} ({j['media_chutes']} ch/j, {j['media_sot']} SOT/j → olhar {linha})"
        )

    return "; ".join(partes)


def formatar_top_assist(ranking, limite=3):
    if not ranking:
        return ""

    candidatos = sorted(
        ranking,
        key=lambda x: x["score_assist"],
        reverse=True
    )[:limite]

    partes = []

    for j in candidatos:
        tag = " + bola parada" if j.get("bola_parada") else ""

        partes.append(
            f"{j['jogador']} ({j['passes_chave']} passes-chave, "
            f"{j['assistencias']} assists{tag})"
        )

    return "; ".join(partes)


def formatar_jogador_em_fase(ranking, limite=3):
    if not ranking:
        return ""

    candidatos = sorted(
        ranking,
        key=lambda x: (x["gols"] * 2) + x["score_chute"],
        reverse=True
    )[:limite]

    partes = []

    for j in candidatos:
        partes.append(
            f"{j['jogador']} ({j['gols']} gols recentes, {j['media_chutes']} ch/j, {j['media_sot']} SOT/j)"
        )

    return "; ".join(partes)



def extrair_odds_match_winner(item_odds):
    """
    Procura mercado Match Winner / vencedor.
    Retorna odds Home, Draw e Away do primeiro bookmaker que tiver esse mercado.
    """
    for bookmaker in item_odds.get("bookmakers", []):
        nome_bookmaker = bookmaker.get("name", "")

        for bet in bookmaker.get("bets", []):
            bet_id = bet.get("id")
            bet_name = normalizar(bet.get("name", ""))

            if bet_id != 1 and "match winner" not in bet_name and "winner" not in bet_name:
                continue

            resultado = {
                "bookmaker": nome_bookmaker,
                "home": None,
                "draw": None,
                "away": None
            }

            for valor in bet.get("values", []):
                nome = normalizar(valor.get("value", ""))
                odd = converter_odd(valor.get("odd"))

                if odd is None:
                    continue

                if nome in ["home", "casa", "1"]:
                    resultado["home"] = odd
                elif nome in ["draw", "empate", "x"]:
                    resultado["draw"] = odd
                elif nome in ["away", "fora", "2"]:
                    resultado["away"] = odd

            if resultado["home"] or resultado["away"]:
                return resultado

    return None


def obter_favorito_por_odd(jogo, odds_por_fixture):
    fixture_id = jogo.get("fixture", {}).get("id")
    odds = odds_por_fixture.get(fixture_id)

    if not odds:
        return None

    casa = nome_time(jogo, "home")
    visitante = nome_time(jogo, "away")

    odd_casa = odds.get("home")
    odd_visitante = odds.get("away")

    if odd_casa is None or odd_visitante is None:
        return None

    if odd_casa <= odd_visitante:
        return {
            "time": casa,
            "adversario": visitante,
            "lado": "home",
            "odd": odd_casa,
            "odd_rival": odd_visitante,
            "bookmaker": odds.get("bookmaker", "")
        }

    return {
        "time": visitante,
        "adversario": casa,
        "lado": "away",
        "odd": odd_visitante,
        "odd_rival": odd_casa,
        "bookmaker": odds.get("bookmaker", "")
    }


def obter_zebras_btts_por_odd(jogo, odds_por_fixture):
    """
    G7.2 — procura lados com odd alta para vencer.
    Não puxa a odd exata de BTTS; usa a odd de resultado como base
    e manda conferir no app o combinado 'vencer + ambos marcam'.
    """
    fixture_id = jogo.get("fixture", {}).get("id")
    odds = odds_por_fixture.get(fixture_id)

    if not odds:
        return []

    casa = nome_time(jogo, "home")
    visitante = nome_time(jogo, "away")

    candidatos = []

    for lado, time, adversario, odd in [
        ("home", casa, visitante, odds.get("home")),
        ("away", visitante, casa, odds.get("away")),
    ]:
        if odd is None:
            continue

        if 3.50 <= odd <= 12.00:
            candidatos.append({
                "time": time,
                "adversario": adversario,
                "lado": lado,
                "odd": odd,
                "bookmaker": odds.get("bookmaker", "")
            })

    return candidatos


def emoji_por_odd_favorito(odd):
    if odd <= 1.60:
        return "🔥"
    if odd <= 2.10:
        return "⚠️"
    return "🧪"


def faixa_por_odd_favorito(odd):
    if odd <= 1.60:
        return "favorito forte"
    if odd <= 2.10:
        return "favorito médio"
    if odd <= 2.50:
        return "favorito leve"
    return "jogo equilibrado"


def linhas_h_por_odd(time_forte, adversario, odd):
    """
    Linhas sugeridas pelo nível de favoritismo real.
    Se a odd é baixa, aceita linha mais pesada.
    Se a odd é perto de 2, usa linhas mais leves.
    """
    if odd <= 1.60:
        return (
            f"{time_forte} +7.5/+8.5 chutes 1T; "
            f"{adversario} -5.5/-7.5 chutes 1T; "
            f"{time_forte} +3/+4 escanteios 1T; "
            f"{adversario} -2/-3 escanteios 1T"
        )

    if odd <= 2.10:
        return (
            f"{time_forte} +5.5/+6.5 chutes 1T; "
            f"{adversario} -6.5/-7.5 chutes 1T; "
            f"{time_forte} +2/+3 escanteios 1T; "
            f"{adversario} -2/-3 escanteios 1T"
        )

    return (
        f"{time_forte} +4.5/+5.5 chutes 1T; "
        f"{adversario} -7.5 chutes 1T; "
        f"{time_forte} +1/+2 escanteios 1T; "
        f"{adversario} -2/-3 escanteios 1T"
    )


def linha_h2_por_odd(time_forte, adversario, odd):
    if odd <= 1.60:
        return (
            f"{time_forte} +2.5 chutes ao gol 1T "
            f"ou {adversario} -1.5 chutes ao gol 1T"
        )

    return (
        f"{time_forte} +1.5/+2.5 chutes ao gol 1T "
        f"ou {adversario} -1.5 chutes ao gol 1T"
    )


def linhas_h21_por_odd(time_forte, adversario, odd):
    if odd <= 1.60:
        return (
            f"{time_forte} +8.5 chutes 1T; "
            f"{adversario} -7.5 chutes 1T; "
            f"{time_forte} +3 escanteios 1T; "
            f"{adversario} -2 escanteios 1T; "
            f"{time_forte} +2.5 chutes ao gol 1T"
        )

    return (
        f"{time_forte} +6.5 chutes 1T; "
        f"{adversario} -7.5 chutes 1T; "
        f"{time_forte} +2 escanteios 1T; "
        f"{adversario} -2 escanteios 1T; "
        f"{time_forte} +1.5/+2.5 chutes ao gol 1T"
    )


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

def eh_time_dominio_1t_agressivo(time_nome):
    return contem_time(time_nome, TIMES_DOMINIO_1T_AGRESSIVO)


def linhas_dominio_1t(time_forte, adversario):
    """
    H1 base — 4 pernas:
    over chutes 1T do dominante + under chutes 1T do rival
    over escanteios 1T do dominante + under escanteios 1T do rival
    """
    if eh_time_dominio_1t_agressivo(time_forte):
        return (
            f"{time_forte} +7.5/+8.5 chutes 1T; "
            f"{adversario} -5.5/-7.5 chutes 1T; "
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
    """
    H2 agressivo — acrescenta chutes ao gol 1T.
    """
    if eh_time_dominio_1t_agressivo(time_forte):
        return (
            f"{time_forte} +2.5 chutes ao gol 1T "
            f"ou {adversario} -1.5 chutes ao gol 1T"
        )

    return (
        f"{time_forte} +1.5/+2.5 chutes ao gol 1T "
        f"ou {adversario} -1.5 chutes ao gol 1T"
    )


def linhas_modelo_print_h2(time_forte, adversario):
    """
    H2.1 — Modelo print Faixa VIP:
    5 pernas no mesmo jogo, como Hoffenheim/City/CRB:
    over chutes 1T + under rival + over escanteios 1T + under rival + over SOT 1T.
    """
    if eh_time_dominio_1t_agressivo(time_forte):
        return (
            f"{time_forte} +8.5 chutes 1T; "
            f"{adversario} -7.5 chutes 1T; "
            f"{time_forte} +3 escanteios 1T; "
            f"{adversario} -2 escanteios 1T; "
            f"{time_forte} +2.5 chutes ao gol 1T"
        )

    return (
        f"{time_forte} +6.5 chutes 1T; "
        f"{adversario} -7.5 chutes 1T; "
        f"{time_forte} +2 escanteios 1T; "
        f"{adversario} -2 escanteios 1T; "
        f"{time_forte} +1.5/+2.5 chutes ao gol 1T"
    )


def deve_sugerir_modelo_print_h2(time_forte, adversario):
    """
    H2.1 — Modelo print Faixa VIP.
    Antes estava restritivo demais e puxava poucos jogos.
    Agora:
    - sugere para todo time cadastrado como domínio 1T;
    - dá linha forte se o time está em TIMES_DOMINIO_1T_AGRESSIVO;
    - evita apenas casos em que o adversário também é muito forte e o time escolhido não é agressivo.
    """
    if not eh_time_dominio_1t(time_forte):
        return False

    if eh_time_dominio_1t_agressivo(adversario) and not eh_time_dominio_1t_agressivo(time_forte):
        return False

    return True


def linhas_modelo_print_aberto(casa, visitante):
    """
    H0 — Modelo aberto Faixa VIP.
    Não tenta adivinhar o favorito só por lista fixa.
    A ideia é mandar o jogo e orientar a leitura no app/bet:
    escolher o favorito real do mercado ou o time que deve começar pressionando.
    """
    return (
        "no app, escolher o favorito/mandante dominante ou o time com menor odd; "
        "montar: TIME ESCOLHIDO +6.5/+8.5 chutes 1T; "
        "RIVAL -6.5/-7.5 chutes 1T; "
        "TIME ESCOLHIDO +2/+3 escanteios 1T; "
        "RIVAL -2/-3 escanteios 1T; "
        "opcional agressivo: TIME ESCOLHIDO +1.5/+2.5 chutes ao gol 1T"
    )


# ============================================================
# GERAÇÃO DOS CANDIDATOS
# ============================================================

def gerar_candidatos(jogos, odds_por_fixture=None, medias_por_time=None, rankings_por_time=None, elencos_por_time=None):
    if odds_por_fixture is None:
        odds_por_fixture = {}

    if medias_por_time is None:
        medias_por_time = {}

    if rankings_por_time is None:
        rankings_por_time = {}

    if elencos_por_time is None:
        elencos_por_time = {}

    resultado = {
        # LUKA
        "[LUKA] A1 — Cantos 10 min | Mandante forte": [],
        "[LUKA] A2 — Cantos 10 min | Visitante favorito": [],

        "[LUKA] B4 — Cartões FT por time | +2/+3 cartões": [],
        "[LUKA] B5 — Cartões individuais | Clássico/jogo quente": [],
        "[FAIXA VIP] B_STATS — Médias reais | cartões FT e 2T": [],

        "[LUKA] C1 — Criador + Finalizador": [],
        "[LUKA] C2 — Gol de Cabeça | Jogos para procurar": [],
        "[LUKA] C3 — Gol de Fora da Área | Jogos para procurar": [],
        "[LUKA] C4 — Roteiro de jogadores | Assistência + gol": [],
        "[LUKA] C9 — Gols e assistências | elenco atualizado": [],
        "[LUKA] C9.1 — Odd 20–60 | roteiro agressivo": [],

        "[LUKA] E1 — Resultado Final | Favoritos para vencer": [],
        "[LUKA] E2 — Resultado Final | Empate candidato": [],

        # FAIXA VIP
        "[FAIXA VIP] G7 — Resultado final + ambos marcam": [],
        "[FAIXA VIP] G7.2 — Zebra/visitante vencer + ambos marcam": [],
        "[FAIXA VIP] C8 — Assistências | Escanteio/falta/lateral": [],
        "[FAIXA VIP] C8.1 — Assistências reais | passes-chave/assists": [],
        "[LUKA] C5 — Assistência de bola parada | escanteio/falta/lateral": [],
        "[LUKA] C6 — Jogador em fase | gols e chutes recentes": []
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
        favorito_odd = obter_favorito_por_odd(jogo, odds_por_fixture)
        medias_home, medias_away = obter_medias_jogo(jogo, medias_por_time)
        rank_home, rank_away = obter_rank_jogadores_jogo(jogo, rankings_por_time)

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

            linha_cards_stats = montar_linha_cartoes_stats(casa, visitante, medias_home, medias_away)
            if linha_cards_stats:
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] B_STATS — Médias reais | cartões FT e 2T"],
                    f"{emoji} {jogo_txt} — {linha_cards_stats}"
                )

            if eh_classico_ou_quente(casa, visitante):
                adicionar_sem_duplicar(
                    resultado["[LUKA] B5 — Cartões individuais | Clássico/jogo quente"],
                    f"🔥 {jogo_txt} — olhar 3-4 jogadores para cartão individual"
                )
        # ====================================================
        # LUKA C2 / C3 — CABEÇA E FORA DA ÁREA POR PERFIL
        # ====================================================

        times_no_jogo = []

        if eh_favorito(casa):
            times_no_jogo.append(casa)

        if eh_favorito(visitante):
            times_no_jogo.append(visitante)

        if favorito_odd and favorito_odd["odd"] <= 2.50:
            if favorito_odd["time"] not in times_no_jogo:
                times_no_jogo.append(favorito_odd["time"])

        # ====================================================
        # LUKA C9 — GOLS E ASSISTÊNCIAS COM ELENCO ATUALIZADO
        # ====================================================

        for lado, time_c9, adversario_c9 in [
            ("home", casa, visitante),
            ("away", visitante, casa),
        ]:
            if not eh_time_prioritario_c9(time_c9):
                continue

            team_id_c9 = id_time(jogo, lado)
            elenco_c9 = elencos_por_time.get(team_id_c9, [])
            perfis_c9 = gerar_perfis_c9_time(time_c9, elenco_c9)

            for linha_c9 in montar_linhas_c9(jogo_txt, time_c9, perfis_c9, adversario_c9):
                adicionar_sem_duplicar(
                    resultado[linha_c9["categoria"]],
                    linha_c9["texto"]
                )

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

        if favorito_odd and favorito_odd["odd"] <= 2.50 and not eh_jogo_equilibrado(casa, visitante):
            emoji = emoji_por_odd_favorito(favorito_odd["odd"])
            adicionar_sem_duplicar(
                resultado["[LUKA] E1 — Resultado Final | Favoritos para vencer"],
                f"{emoji} {jogo_txt} — favorito por odd: {favorito_odd['time']} @{favorito_odd['odd']:.2f} vencer / pagamento antecipado"
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
        # FAIXA VIP G7 — RESULTADO + AMBOS MARCAM
        # ====================================================

        if eh_liga_aberta_gols(liga, pais) or eh_time_btts_vencer(casa) or eh_time_btts_vencer(visitante) or favorito_odd:
            if favorito_odd and favorito_odd["odd"] <= 2.80:
                emoji = emoji_por_odd_favorito(favorito_odd["odd"])
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] G7 — Resultado final + ambos marcam"],
                    f"{emoji} {jogo_txt} — favorito por odd: {favorito_odd['time']} @{favorito_odd['odd']:.2f} vencer + ambos marcam"
                )

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

            for zebra in obter_zebras_btts_por_odd(jogo, odds_por_fixture):
                texto_lado = "visitante/zebra" if zebra["lado"] == "away" else "mandante zebra"
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] G7.2 — Zebra/visitante vencer + ambos marcam"],
                    f"🧪 {jogo_txt} — {texto_lado}: olhar {zebra['time']} vencer + ambos marcam; odd resultado @{zebra['odd']:.2f}; stake simbólica"
                )

        # ====================================================
        # FAIXA VIP C8 — ASSISTÊNCIAS / BOLA PARADA
        # ====================================================

        for time_forte in times_no_jogo:
            emoji = "⚠️"
            ranking_time = escolher_rank_do_time(time_forte, casa, visitante, rank_home, rank_away)

            adicionar_sem_duplicar(
                resultado["[FAIXA VIP] C8 — Assistências | Escanteio/falta/lateral"],
                f"{emoji} {jogo_txt} — {time_forte}: {sugestao_assistencia_time(time_forte)}"
            )

            top_assist = formatar_top_assist(ranking_time)
            if top_assist:
                adicionar_sem_duplicar(
                    resultado["[FAIXA VIP] C8.1 — Assistências reais | passes-chave/assists"],
                    f"{emoji} {jogo_txt} — {time_forte}: {top_assist}"
                )

            adicionar_sem_duplicar(
                resultado["[LUKA] C5 — Assistência de bola parada | escanteio/falta/lateral"],
                f"🧪 {jogo_txt} — {time_forte}: assistência de bola parada/lateral longo; combinar com atacante ou zagueiro forte de cabeça"
            )

            fase = formatar_jogador_em_fase(ranking_time)
            if fase:
                adicionar_sem_duplicar(
                    resultado["[LUKA] C6 — Jogador em fase | gols e chutes recentes"],
                    f"🧪 {jogo_txt} — {time_forte}: {fase}"
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

        "[LUKA] B4 — Cartões FT por time | +2/+3 cartões": 14,
        "[LUKA] B5 — Cartões individuais | Clássico/jogo quente": 8,
        "[FAIXA VIP] B_STATS — Médias reais | cartões FT e 2T": 12,

        "[LUKA] C1 — Criador + Finalizador": 6,
        "[LUKA] C2 — Gol de Cabeça | Jogos para procurar": 8,
        "[LUKA] C3 — Gol de Fora da Área | Jogos para procurar": 8,
        "[LUKA] C4 — Roteiro de jogadores | Assistência + gol": 10,
        "[LUKA] C9 — Gols e assistências | elenco atualizado": 12,
        "[LUKA] C9.1 — Odd 20–60 | roteiro agressivo": 8,

        "[LUKA] E1 — Resultado Final | Favoritos para vencer": 8,
        "[LUKA] E2 — Resultado Final | Empate candidato": 6,

        # FAIXA VIP
        "[FAIXA VIP] G7 — Resultado final + ambos marcam": 10,
        "[FAIXA VIP] G7.2 — Zebra/visitante vencer + ambos marcam": 14,
        "[FAIXA VIP] C8 — Assistências | Escanteio/falta/lateral": 10,
        "[FAIXA VIP] C8.1 — Assistências reais | passes-chave/assists": 10,
        "[LUKA] C5 — Assistência de bola parada | escanteio/falta/lateral": 8,
        "[LUKA] C6 — Jogador em fase | gols e chutes recentes": 8
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
    odds_por_fixture = buscar_odds_hoje()
    medias_por_time = buscar_medias_times_do_dia(jogos, odds_por_fixture)
    rankings_por_time = buscar_rank_jogadores_times_do_dia(jogos, odds_por_fixture)
    elencos_por_time = buscar_elencos_prioritarios_do_dia(jogos)

    if not jogos:
        print("Nenhum jogo encontrado.")
    else:
        candidatos = gerar_candidatos(jogos, odds_por_fixture, medias_por_time, rankings_por_time, elencos_por_time)
        candidatos = limitar_lista(candidatos)
        salvar_jogos_json(candidatos)
