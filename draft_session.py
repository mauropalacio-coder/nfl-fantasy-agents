from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent

def run_draft_session():
    print("\n" + "="*50)
    print("   NFL FANTASY DRAFT 2026 - ASISTENTE DE MAURO")
    print("="*50)
    print("Draft serpentina | 15 rondas | 4 participantes")
    print("Presiona Enter para avanzar a la siguiente ronda\n")

    # Inicializar agentes
    data_agent = DataAgent()
    data_agent.load_data()
    draft_agent = DraftAgent(data_agent)

    for round_number in range(1, 16):
        pick_position = draft_agent.get_pick_position(round_number)
        picks_before_mauro = pick_position - 1
        picks_after_mauro = 4 - pick_position

        print("\n" + "="*50)
        print(f"RONDA {round_number} de 15 | Tu pick: #{pick_position} de 4")
        print("="*50)
        print("\nGenerando recomendaciones...\n")

        recomendacion = draft_agent.recommend(round_number=round_number)
        print(recomendacion)

        # Extraer jugadores recomendados para simular picks de amigos
        lineas = recomendacion.split("\n")
        opciones = []
        for linea in lineas:
            if linea.strip().startswith("OPCION") and "|" in linea:
                partes = linea.split("|")
                if len(partes) >= 2:
                    nombre = partes[0].split(":")[-1].strip()
                    opciones.append(nombre)

        if round_number < 15:
            input("\nPresiona Enter cuando hayas hecho tu pick para continuar...")

            # Simular que los amigos tomaron las mejores opciones disponibles
            # Picks antes de Mauro en esta ronda ya fueron tomados
            # Picks despues de Mauro en esta ronda tambien se van
            jugadores_tomados = picks_before_mauro + picks_after_mauro

            for i in range(min(jugadores_tomados, len(opciones))):
                nombre = opciones[i]
                # Buscar el jugador en la base para marcarlo como draftado
                results = data_agent.get_player_info(nombre)
                if results:
                    draft_agent.mark_as_drafted(results[0]["id"])

            # Tambien marcar la opcion que presumiblemente tomo Mauro
            # (la opcion 1 menos los que ya se fueron antes)
            idx_mauro = picks_before_recomendados = picks_before_mauro
            if idx_mauro < len(opciones):
                nombre_mauro = opciones[idx_mauro]
                results = data_agent.get_player_info(nombre_mauro)
                if results:
                    draft_agent.add_to_roster(
                        results[0]["id"],
                        results[0]["name"],
                        results[0]["position"]
                    )
        else:
            print("\n¡Draft completado! Buena suerte en la temporada. 🏈")

if __name__ == "__main__":
    run_draft_session()