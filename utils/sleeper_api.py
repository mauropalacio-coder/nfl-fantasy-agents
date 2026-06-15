import requests

BASE_URL = "https://api.sleeper.app/v1"

def get_all_players():
    """Trae todos los jugadores de la NFL desde Sleeper."""
    url = f"{BASE_URL}/players/nfl"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener jugadores: {response.status_code}")

def get_nfl_state():
    """Trae el estado actual de la temporada NFL."""
    url = f"{BASE_URL}/state/nfl"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener estado NFL: {response.status_code}")

def get_player_stats(season, season_type="regular"):
    """Trae stats de todos los jugadores para una temporada."""
    url = f"{BASE_URL}/stats/nfl/regular/{season}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener stats {season}: {response.status_code}")

def get_player_projections(season, week=1):
    """Trae proyecciones de jugadores para una semana."""
    url = f"{BASE_URL}/projections/nfl/{season}/{week}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener proyecciones: {response.status_code}")
    
def get_player_stats_multiyear(seasons=[2023, 2024, 2025]):
    """Trae stats de multiples temporadas."""
    all_stats = {}
    for season in seasons:
        print(f"  Descargando stats {season}...")
        try:
            stats = get_player_stats(season)
            all_stats[season] = stats
        except Exception as e:
            print(f"  Error en {season}: {e}")
    return all_stats