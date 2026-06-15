from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent

def main():
    data_agent = DataAgent()
    data_agent.load_data()
    data_agent.load_player_rankings(seasons=[2023, 2024, 2025])

    draft_agent = DraftAgent(data_agent)

    print("\n=== DRAFT AGENT CON RANKINGS REALES ===")
    print("Ronda 1 - Pick #3 de 4\n")
    print(draft_agent.recommend(round_number=1))

if __name__ == "__main__":
    main()