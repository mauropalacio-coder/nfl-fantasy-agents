from utils.sleeper_api import get_all_players, get_nfl_state

def main():
    print("Probando conexión a Sleeper API...")
    
    # Probar estado de la temporada
    state = get_nfl_state()
    print(f"Temporada actual: {state['season']}")
    print(f"Semana actual: {state['week']}")
    print(f"Tipo de temporada: {state['season_type']}")
    
    # Probar jugadores
    print("\nObteniendo jugadores...")
    players = get_all_players()
    print(f"Total de jugadores en la base: {len(players)}")

if __name__ == "__main__":
    main()
    
from agents.data_agent import DataAgent

def main():
    agent = DataAgent()
    agent.load_data()

    # Info de la temporada
    season = agent.get_season_info()
    print(f"\nTemporada: {season['season']} | Semana: {season['week']} | Estado: {season['season_type']}")

    # Buscar a Brock Purdy
    print("\nBuscando a Brock Purdy...")
    purdy = agent.get_player_info("Brock Purdy")
    for p in purdy:
        print(f"  {p['name']} | {p['position']} | {p['team']} | Edad: {p['age']} | Años exp: {p['years_exp']}")

    # QBs activos
    print("\nQBs activos en la liga:")
    qbs = agent.get_players_by_position("QB")
    for qb in qbs[:10]:  # Solo los primeros 10
        print(f"  {qb['name']} | {qb['team']}")

if __name__ == "__main__":
    main()