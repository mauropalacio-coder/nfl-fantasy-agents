from agents.data_agent import DataAgent
from agents.weekly_agent import WeeklyAgent

def main():
    data_agent = DataAgent()
    data_agent.load_data()

    weekly_agent = WeeklyAgent(data_agent)

    # Roster de Mauro
    roster = [
        {"name": "Brock Purdy", "position": "QB", "team": "SF", "age": 26, "years_exp": 4},
        {"name": "Christian McCaffrey", "position": "RB", "team": "SF", "age": 29, "years_exp": 9},
        {"name": "Saquon Barkley", "position": "RB", "team": "PHI", "age": 29, "years_exp": 8},
        {"name": "CeeDee Lamb", "position": "WR", "team": "DAL", "age": 26, "years_exp": 5},
        {"name": "Amon-Ra St. Brown", "position": "WR", "team": "DET", "age": 25, "years_exp": 4},
        {"name": "Sam LaPorta", "position": "TE", "team": "DET", "age": 24, "years_exp": 2},
        {"name": "Josh Jacobs", "position": "RB", "team": "GB", "age": 27, "years_exp": 6},
        {"name": "Jaylen Warren", "position": "RB", "team": "PIT", "age": 26, "years_exp": 3},
        {"name": "Rashid Shaheed", "position": "WR", "team": "NO", "age": 26, "years_exp": 3},
        {"name": "Jake Elliott", "position": "K", "team": "PHI", "age": 29, "years_exp": 8},
        {"name": "San Francisco 49ers", "position": "DEF", "team": "SF", "age": None, "years_exp": None},
    ]

    # Roster manual del rival
    opponent_roster = [
        {"name": "Patrick Mahomes", "position": "QB", "team": "KC"},
        {"name": "Derrick Henry", "position": "RB", "team": "BAL"},
        {"name": "Alvin Kamara", "position": "RB", "team": "NO"},
        {"name": "Davante Adams", "position": "WR", "team": "LAR"},
        {"name": "Stefon Diggs", "position": "WR", "team": "HOU"},
        {"name": "Travis Kelce", "position": "TE", "team": "KC"},
        {"name": "Tony Pollard", "position": "RB", "team": "TEN"},
        {"name": "Justin Tucker", "position": "K", "team": "BAL"},
        {"name": "Dallas Cowboys", "position": "DEF", "team": "DAL"},
    ]

    print("\n=== WEEKLY LINEUP AGENT - SEMANA 5 ===")
    print("Rival: Amigo 2\n")

    recomendacion = weekly_agent.recommend_lineup(
        roster=roster,
        week=5,
        opponent_name="Amigo 2",
        opponent_roster=opponent_roster,
        opponent_image_path=None
    )
    print(recomendacion)

if __name__ == "__main__":
    main()