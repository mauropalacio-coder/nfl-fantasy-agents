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
        self.rankings = {}
        self.def_rankings = {}

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

    def get_player_info_by_id(self, player_id):
        """Busca un jugador por su ID."""
        return self.players.get(player_id, None)

    def get_players_by_position(self, position):
        return [
            {
                "id": pid,
                "name": info.get("full_name"),
                "team": info.get("team"),
                "age": info.get("age"),
                "years_exp": info.get("years_exp", 0),
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

    def get_top_players_by_position(self, position, limit=20):
        """Retorna los jugadores de una posicion ordenados por experiencia."""
        players = [
            {
                "id": pid,
                "name": info.get("full_name"),
                "team": info.get("team"),
                "age": info.get("age"),
                "years_exp": info.get("years_exp", 0),
                "position": info.get("position"),
            }
            for pid, info in self.players.items()
            if info.get("position") == position
        ]
        players.sort(key=lambda x: x.get("years_exp") or 0, reverse=True)
        return players[:limit]

    def get_draft_pool(self, excluded_ids=None):
        """Retorna el pool de draft ordenado por experiencia (fallback)."""
        if excluded_ids is None:
            excluded_ids = []

        pool = {}
        for position in ["QB", "RB", "WR", "TE", "K", "DEF"]:
            players = [
                {
                    "id": pid,
                    "name": info.get("full_name"),
                    "team": info.get("team"),
                    "age": info.get("age"),
                    "years_exp": info.get("years_exp", 0),
                }
                for pid, info in self.players.items()
                if info.get("position") == position
                and pid not in excluded_ids
            ]
            players.sort(key=lambda x: x.get("years_exp") or 0, reverse=True)
            pool[position] = players

        return pool

    def load_player_rankings(self, seasons=[2023, 2024, 2025], min_games=6):
        """Calcula rankings de jugadores por promedio de puntos fantasy."""
        from utils.sleeper_api import get_player_stats_multiyear

        TEAM_NAMES = {
            "TEAM_ARI": "Arizona Cardinals", "TEAM_ATL": "Atlanta Falcons",
            "TEAM_BAL": "Baltimore Ravens", "TEAM_BUF": "Buffalo Bills",
            "TEAM_CAR": "Carolina Panthers", "TEAM_CHI": "Chicago Bears",
            "TEAM_CIN": "Cincinnati Bengals", "TEAM_CLE": "Cleveland Browns",
            "TEAM_DAL": "Dallas Cowboys", "TEAM_DEN": "Denver Broncos",
            "TEAM_DET": "Detroit Lions", "TEAM_GB": "Green Bay Packers",
            "TEAM_HOU": "Houston Texans", "TEAM_IND": "Indianapolis Colts",
            "TEAM_JAX": "Jacksonville Jaguars", "TEAM_KC": "Kansas City Chiefs",
            "TEAM_LAC": "LA Chargers", "TEAM_LAR": "LA Rams",
            "TEAM_LV": "Las Vegas Raiders", "TEAM_MIA": "Miami Dolphins",
            "TEAM_MIN": "Minnesota Vikings", "TEAM_NE": "New England Patriots",
            "TEAM_NO": "New Orleans Saints", "TEAM_NYG": "New York Giants",
            "TEAM_NYJ": "New York Jets", "TEAM_PHI": "Philadelphia Eagles",
            "TEAM_PIT": "Pittsburgh Steelers", "TEAM_SEA": "Seattle Seahawks",
            "TEAM_SF": "San Francisco 49ers", "TEAM_TB": "Tampa Bay Buccaneers",
            "TEAM_TEN": "Tennessee Titans", "TEAM_WAS": "Washington Commanders",
        }

        print("Cargando rankings historicos de jugadores...")
        all_stats = get_player_stats_multiyear(seasons)

        player_scores = {}
        def_scores = {}

        for season, stats in all_stats.items():
            for player_id, data in stats.items():
                pts = data.get("pts_std", 0) or 0
                gp = data.get("gp", 0) or 0

                if player_id.startswith("TEAM_"):
                    if gp >= min_games and pts > 0:
                        pts_per_game = pts / gp
                        if player_id not in def_scores:
                            def_scores[player_id] = []
                        def_scores[player_id].append(pts_per_game)
                else:
                    if gp >= min_games and pts > 0:
                        pts_per_game = pts / gp
                        if player_id not in player_scores:
                            player_scores[player_id] = []
                        player_scores[player_id].append(pts_per_game)

        player_avg = {
            pid: sum(scores) / len(scores)
            for pid, scores in player_scores.items()
        }

        def_avg = {
            pid: {
                "name": TEAM_NAMES.get(pid, pid),
                "avg_pts": sum(scores) / len(scores)
            }
            for pid, scores in def_scores.items()
        }

        # Enriquecer jugadores activos con su promedio de puntos
        self.rankings = {}
        for player_id, avg in player_avg.items():
            info = self.players.get(player_id)
            if info:
                self.rankings[player_id] = {
                    "id": player_id,
                    "name": info.get("full_name"),
                    "position": info.get("position"),
                    "team": info.get("team"),
                    "age": info.get("age"),
                    "avg_pts": round(avg, 1),
                }

        self.def_rankings = def_avg
        print(f"Rankings cargados: {len(self.rankings)} jugadores activos con historial.")
        return self.rankings

    def get_ranked_draft_pool(self, excluded_ids=None):
        """Retorna el pool de draft ordenado por promedio de puntos reales."""
        if excluded_ids is None:
            excluded_ids = []

        if not self.rankings:
            print("Rankings no cargados. Llama a load_player_rankings() primero.")
            return {}

        pool = {}
        for position in ["QB", "RB", "WR", "TE", "K"]:
            players = [
                p for pid, p in self.rankings.items()
                if p["position"] == position
                and pid not in excluded_ids
            ]
            players.sort(key=lambda x: x["avg_pts"], reverse=True)
            pool[position] = players

        # Agregar defensas normalizadas por partido
        if self.def_rankings:
            defs = [
                {
                    "name": v["name"],
                    "team": k.replace("TEAM_", ""),
                    "position": "DEF",
                    "avg_pts": round(v["avg_pts"] / 17, 1)
                }
                for k, v in self.def_rankings.items()
            ]
            defs.sort(key=lambda x: x["avg_pts"], reverse=True)
            pool["DEF"] = defs

        return pool