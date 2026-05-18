import json
import os
from datetime import datetime, timedelta
from utils.sleeper_api import get_all_players, get_nfl_state
from utils.claude_client import ask_claude

# Posiciones relevantes para fantasy
RELEVANT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]

# Cache local
CACHE_DIR = "data"
PLAYERS_CACHE_FILE = os.path.join(CACHE_DIR, "players_cache.json")
CACHE_EXPIRY_HOURS = 24

class DataAgent:
    def __init__(self):
        self.players = {}
        self.nfl_state = {}

    def _is_cache_valid(self):
        if not os.path.exists(PLAYERS_CACHE_FILE):
            return False
        modified_time = datetime.fromtimestamp(os.path.getmtime(PLAYERS_CACHE_FILE))
        return datetime.now() - modified_time < timedelta(hours=CACHE_EXPIRY_HOURS)

    def _save_cache(self, data):
        with open(PLAYERS_CACHE_FILE, "w") as f:
            json.dump(data, f)
        print("Cache guardado localmente.")

    def _load_cache(self):
        with open(PLAYERS_CACHE_FILE, "r") as f:
            return json.load(f)

    def load_data(self, force_refresh=False):
        self.nfl_state = get_nfl_state()
        if not force_refresh and self._is_cache_valid():
            print("Cargando jugadores desde cache local...")
            self.players = self._load_cache()
            print(f"Jugadores cargados desde cache: {len(self.players)}")
        else:
            print("Cargando jugadores desde Sleeper API...")
            all_players = get_all_players()
            self.players = {
                player_id: info
                for player_id, info in all_players.items()
                if info.get("position") in RELEVANT_POSITIONS
                and info.get("status") == "Active"
                and info.get("team") is not None
            }
            self._save_cache(self.players)
            print(f"Jugadores activos cargados: {len(self.players)}")
        return self.players

    def get_player_info(self, name):
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
        return {
            "season": self.nfl_state.get("season"),
            "week": self.nfl_state.get("week"),
            "season_type": self.nfl_state.get("season_type"),
        }

    def analyze_player(self, name):
        players = self.get_player_info(name)
        if not players:
            return f"No se encontro ningun jugador con el nombre '{name}'."
        player = players[0]
        prompt = f"""
        Analiza a este jugador de NFL para fantasy football temporada 2026:
        Nombre: {player['name']}
        Posicion: {player['position']}
        Equipo: {player['team']}
        Edad: {player['age']}
        Anos de experiencia: {player['years_exp']}
        Dame un analisis breve con:
        - Valor general para fantasy
        - Fortalezas y riesgos
        - Ronda recomendada de draft
        - Veredicto final
        """
        system_prompt = "Eres un experto en NFL fantasy football. Tus analisis son concisos, directos y utiles para tomar decisiones de draft."
        analysis = ask_claude(prompt, system_prompt=system_prompt)
        return {
            "player": player,
            "analysis": analysis
        }