import json
import os
from datetime import datetime

ROSTER_FILE = os.path.join("data", "my_roster.json")

def load_roster():
    """Carga el roster desde el archivo JSON."""
    if not os.path.exists(ROSTER_FILE):
        return []
    with open(ROSTER_FILE, "r") as f:
        data = json.load(f)
    return data.get("players", [])

def save_roster(players):
    """Guarda el roster en el archivo JSON."""
    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "players": players
    }
    with open(ROSTER_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Roster guardado: {len(players)} jugadores.")

def add_player(name, position, team, age=None, years_exp=None, player_id=None):
    """Agrega un jugador al roster."""
    players = load_roster()
    player = {
        "id": player_id or f"manual_{name.lower().replace(' ', '_')}",
        "name": name,
        "position": position,
        "team": team,
        "age": age,
        "years_exp": years_exp,
    }
    # Verificar que no exista ya
    existing = [p for p in players if p["name"].lower() == name.lower()]
    if existing:
        print(f"{name} ya esta en el roster.")
        return players
    players.append(player)
    save_roster(players)
    return players

def remove_player(name):
    """Elimina un jugador del roster por nombre."""
    players = load_roster()
    original_count = len(players)
    players = [p for p in players if p["name"].lower() != name.lower()]
    if len(players) < original_count:
        save_roster(players)
        print(f"{name} eliminado del roster.")
    else:
        print(f"{name} no encontrado en el roster.")
    return players

def show_roster():
    """Muestra el roster actual."""
    players = load_roster()
    if not players:
        print("Roster vacio.")
        return
    print(f"\nTU ROSTER ({len(players)} jugadores):")
    for p in sorted(players, key=lambda x: x["position"]):
        print(f"  {p['position']:4} | {p['name']:25} | {p['team']}")