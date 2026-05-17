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