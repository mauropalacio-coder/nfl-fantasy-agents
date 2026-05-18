from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent

def main():
    data_agent = DataAgent()
    data_agent.load_data()

    draft_agent = DraftAgent(data_agent)

    # Simular ronda 1
    print("\n=== RONDA 1 - Pick #3 de 4 ===")
    print(draft_agent.recommend(round_number=1))

    # Simular que Mauro toma a CeeDee Lamb
    draft_agent.add_to_roster("2374", "CeeDee Lamb", "WR")

    # Simular ronda 2
    print("\n=== RONDA 2 - Pick #2 de 4 ===")
    print(draft_agent.recommend(round_number=2))

if __name__ == "__main__":
    main()