import json
import os
from datetime import datetime

LEAGUE_ROSTER_FILE = os.path.join("data", "league_rosters.json")

def load_league_rosters():
    """Carga todos los rosters de la liga."""
    if not os.path.exists(LEAGUE_ROSTER_FILE):
        return {}
    with open(LEAGUE_ROSTER_FILE, "r") as f:
        data = json.load(f)
    return data.get("participants", {})

def save_league_rosters(participants):
    """Guarda todos los rosters de la liga."""
    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "participants": participants
    }
    with open(LEAGUE_ROSTER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_drafted_players():
    """Retorna todos los jugadores que estan en algun roster de la liga."""
    participants = load_league_rosters()
    drafted = []
    for name, roster in participants.items():
        for player in roster.get("starters", []):
            drafted.append(player.get("id", ""))
        for player in roster.get("bench", []):
            drafted.append(player.get("id", ""))
    return [d for d in drafted if d]

def add_player_to_roster(participant, player, slot="bench"):
    """Agrega un jugador al roster de un participante."""
    participants = load_league_rosters()
    if participant not in participants:
        participants[participant] = {"starters": [], "bench": []}
    
    # Verificar que no este ya en el roster
    all_players = participants[participant]["starters"] + participants[participant]["bench"]
    if any(p["name"].lower() == player["name"].lower() for p in all_players):
        return False, f"{player['name']} ya esta en el roster de {participant}."
    
    participants[participant][slot].append(player)
    save_league_rosters(participants)
    return True, f"{player['name']} agregado a {slot} de {participant}."

def remove_player_from_roster(participant, player_name):
    """Elimina un jugador del roster de un participante."""
    participants = load_league_rosters()
    if participant not in participants:
        return False, f"{participant} no encontrado."
    
    for slot in ["starters", "bench"]:
        participants[participant][slot] = [
            p for p in participants[participant][slot]
            if p["name"].lower() != player_name.lower()
        ]
    
    save_league_rosters(participants)
    return True, f"{player_name} eliminado del roster de {participant}."

def move_player(participant, player_name, to_slot):
    """Mueve un jugador entre starters y bench."""
    participants = load_league_rosters()
    if participant not in participants:
        return False, f"{participant} no encontrado."
    
    from_slot = "bench" if to_slot == "starters" else "starters"
    player = None
    
    for p in participants[participant][from_slot]:
        if p["name"].lower() == player_name.lower():
            player = p
            break
    
    if not player:
        return False, f"{player_name} no encontrado en {from_slot} de {participant}."
    
    participants[participant][from_slot].remove(player)
    participants[participant][to_slot].append(player)
    save_league_rosters(participants)
    return True, f"{player_name} movido a {to_slot} de {participant}."

def get_participant_roster(participant):
    """Retorna el roster completo de un participante."""
    participants = load_league_rosters()
    return participants.get(participant, {"starters": [], "bench": []})

def get_participant_names():
    """Retorna los nombres de los participantes."""
    participants = load_league_rosters()
    return list(participants.keys())