from agents.data_agent import DataAgent
from agents.waiver_agent import WaiverAgent

def main():
    data_agent = DataAgent()
    data_agent.load_data()
    data_agent.load_player_rankings(seasons=[2023, 2024, 2025])

    waiver_agent = WaiverAgent(data_agent)

    # Roster simulado de Mauro
    roster = [
        {"id": "4039", "name": "Brock Purdy", "position": "QB", "team": "SF"},
        {"id": "4866", "name": "Christian McCaffrey", "position": "RB", "team": "SF"},
        {"id": "4035", "name": "Saquon Barkley", "position": "RB", "team": "PHI"},
        {"id": "6797", "name": "CeeDee Lamb", "position": "WR", "team": "DAL"},
        {"id": "7547", "name": "Amon-Ra St. Brown", "position": "WR", "team": "DET"},
        {"id": "7564", "name": "Sam LaPorta", "position": "TE", "team": "DET"},
        {"id": "5012", "name": "Josh Jacobs", "position": "RB", "team": "GB"},
        {"id": "6801", "name": "Jaylen Warren", "position": "RB", "team": "PIT"},
        {"id": "6790", "name": "Rashid Shaheed", "position": "WR", "team": "NO"},
        {"id": "3448", "name": "Jake Elliott", "position": "K", "team": "PHI"},
        {"id": "TEAM_SF", "name": "San Francisco 49ers", "position": "DEF", "team": "SF"},
    ]

    print("\n=== WAIVER AGENT ===")
    print("Posicion en el wire: #3 de 4")
    print("Motivo: Lesion de Jaylen Warren\n")

    recomendacion = waiver_agent.recommend(
        my_roster=roster,
        waiver_position=3,
        total_teams=4,
        trigger="Jaylen Warren se lesiono - necesitas RB de banca"
    )
    print(recomendacion)

if __name__ == "__main__":
    main()