import json
from utils.sleeper_api import get_all_players, get_nfl_state

# Posiciones relevantes para fantasy
RELEVANT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]

class DataAgent:
    def __init__(self):
        self.players = {}
        self.nfl_state = {}

    def load_data(self):
        """Carga y filtra jugadores relevantes para fantasy."""
        print("Cargando datos de jugadores...")
        all_players = get_all_players()
        self.nfl_state = get_nfl_state()

        # Filtrar solo jugadores activos y posiciones relevantes
        self.players = {
            player_id: info
             for player_id, info in all_players.items()
            if info.get("position") in RELEVANT_POSITIONS
            and info.get("status") == "Active"
            and info.get("team") is not None
}

        print(f"Jugadores activos cargados: {len(self.players)}")
        return self.players

    def get_player_info(self, name):
        """Busca un jugador por nombre."""
        name_lower = name.lower()
        results = []
        for player_id, info in self.players.items():
            full_name = info.get("full_name", "").lower()
            if name_lower in full_name:
                results.append({
                    "id": player_id,
                    "name": info.get("full_name"),
                    "position": info.get("position"),
                    "team": info.get("team"),
                    "age": info.get("age"),
                    "years_exp": info.get("years_exp"),
                })
        return results

    def get_players_by_position(self, position):
        """Retorna todos los jugadores activos de una posición."""
        return [
            {
                "id": pid,
                "name": info.get("full_name"),
                "team": info.get("team"),
                "age": info.get("age"),
                "years_exp": info.get("years_exp"),
            }
            for pid, info in self.players.items()
            if info.get("position") == position
        ]

    def get_season_info(self):
        """Retorna el estado actual de la temporada."""
        return {
            "season": self.nfl_state.get("season"),
            "week": self.nfl_state.get("week"),
            "season_type": self.nfl_state.get("season_type"),
        }