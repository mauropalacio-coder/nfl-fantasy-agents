from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent

def find_player_id(data_agent, name):
    """Busca el ID de un jugador por nombre."""
    results = data_agent.get_player_info(name)
    if results:
        return results[0]["id"], results[0]["name"], results[0]["position"]
    return None, None, None

def get_input(prompt):
    """Pide input al usuario y valida que no este vacio."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Debes ingresar algo. Intenta de nuevo.")

def run_draft_session():
    print("\n" + "="*50)
    print("   NFL FANTASY DRAFT 2026 - ASISTENTE DE MAURO")
    print("="*50)

    # Inicializar agentes
    data_agent = DataAgent()
    data_agent.load_data()
    draft_agent = DraftAgent(data_agent)

    current_round = 1
    pick_in_round = 0
    mauro_pick_position = draft_agent.get_pick_position(current_round)

    print(f"\nDraft serpentina | 15 rondas | 4 participantes")
    print(f"Mauro empieza en pick #{mauro_pick_position} de cada ronda impar\n")

    while current_round <= 15:
        pick_in_round += 1
        mauro_pick_position = draft_agent.get_pick_position(current_round)

        if pick_in_round == mauro_pick_position:
            # Turno de Mauro
            print("\n" + "-"*50)
            print(f"RONDA {current_round} - TURNO DE MAURO (Pick #{pick_in_round} de 4)")
            print("-"*50)
            print("\nGenerando recomendaciones...\n")

            recomendacion = draft_agent.recommend(round_number=current_round)
            print(recomendacion)

            # Mauro ingresa su pick
            nombre = get_input("\n¿A quien drafteas? (escribe el nombre del jugador)\n> ")
            player_id, player_name, position = find_player_id(data_agent, nombre)

            if player_id:
                draft_agent.add_to_roster(player_id, player_name, position)
                print(f"✓ {player_name} ({position}) agregado a tu roster")
            else:
                print(f"Jugador '{nombre}' no encontrado en la base. Ingresalo manualmente:")
                position = get_input("Posicion (QB/RB/WR/TE/K/DEF): ").upper()
                draft_agent.add_to_roster(f"manual_{nombre}", nombre, position)
                print(f"✓ {nombre} ({position}) agregado manualmente a tu roster")

        else:
            # Turno de un amigo
            print(f"\nRonda {current_round} - Pick #{pick_in_round} de 4 (amigo)")
            nombre = get_input("¿Que jugador tomo tu amigo? (nombre o 'skip')\n> ")

            if nombre.lower() != "skip":
                player_id, player_name, _ = find_player_id(data_agent, nombre)
                if player_id:
                    draft_agent.mark_as_drafted(player_id)
                    print(f"  Marcado como draftado: {player_name}")
                else:
                    print(f"  Jugador '{nombre}' no encontrado, continuando...")

        # Avanzar ronda cuando se completaron 4 picks
        if pick_in_round == 4:
            pick_in_round = 0
            current_round += 1
            if current_round <= 15:
                print(f"\n{'='*50}")
                print(f"INICIANDO RONDA {current_round}")
                print(f"{'='*50}")

    # Mostrar roster final
    print("\n" + "="*50)
    print("DRAFT COMPLETADO - ROSTER FINAL DE MAURO")
    print("="*50)
    for p in draft_agent.my_roster:
        print(f"  {p['position']:4} | {p['name']}")

if __name__ == "__main__":
    run_draft_session()