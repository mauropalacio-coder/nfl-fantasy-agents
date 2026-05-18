from agents.data_agent import DataAgent

def main():
    agent = DataAgent()
    agent.load_data()

    season = agent.get_season_info()
    print(f"\nTemporada: {season['season']} | Semana: {season['week']} | Estado: {season['season_type']}")

    print("\nBuscando a Brock Purdy...")
    purdy = agent.get_player_info("Brock Purdy")
    for p in purdy:
        print(f"  {p['name']} | {p['position']} | {p['team']} | Edad: {p['age']} | Años exp: {p['years_exp']}")

    print("\nQBs activos en la liga:")
    qbs = agent.get_players_by_position("QB")
    print(f"  Total: {len(qbs)} QBs")

if __name__ == "__main__":
    main()