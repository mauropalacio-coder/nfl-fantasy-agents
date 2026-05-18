from agents.data_agent import DataAgent
from utils.claude_client import ask_claude

def main():
    agent = DataAgent()
    agent.load_data()

    season = agent.get_season_info()
    print(f"\nTemporada: {season['season']} | Semana: {season['week']} | Estado: {season['season_type']}")

    # Obtener info de Brock Purdy
    print("\nAnalizando a Brock Purdy...")
    purdy = agent.get_player_info("Brock Purdy")[0]

    # Pedirle a Claude que analice al jugador
    prompt = f"""
    Analiza a este jugador de NFL para fantasy football:
    
    Nombre: {purdy['name']}
    Posición: {purdy['position']}
    Equipo: {purdy['team']}
    Edad: {purdy['age']}
    Años de experiencia: {purdy['years_exp']}
    
    Dame un análisis breve de su valor para fantasy en la temporada 2026.
    """

    respuesta = ask_claude(prompt, system_prompt="Eres un experto en NFL fantasy football. Tus análisis son concisos y directos.")
    print(respuesta)

if __name__ == "__main__":
    main()