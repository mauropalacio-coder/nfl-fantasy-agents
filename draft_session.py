from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent

def run_draft_session():
    print("\n" + "="*50)
    print("   NFL FANTASY DRAFT 2026 - ASISTENTE DE MAURO")
    print("="*50)
    print("Draft serpentina | 15 rondas | 4 participantes")
    print("Presiona Enter para avanzar a la siguiente ronda\n")

    data_agent = DataAgent()
    data_agent.load_data()
    data_agent.load_player_rankings(seasons=[2023, 2024, 2025])
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

        # Extraer nombres de jugadores recomendados
        opciones = []
        for linea in recomendacion.split("\n"):
            linea_clean = linea.strip()
            # Detectar lineas que empiecen con OPCION (con o sin acento, con o sin **)
            linea_norm = linea_clean.replace("**", "").replace("Ó", "O").replace("ó", "o")
            if linea_norm.upper().startswith("OPCION") and "|" in linea_norm:
                partes = linea_norm.split("|")
                if len(partes) >= 2:
                    nombre = partes[0].split(":")[-1].strip()
                    if nombre:
                        opciones.append(nombre)

        if round_number < 15:
            input("\nPresiona Enter cuando hayas hecho tu pick para continuar...")

            # Marcar jugadores tomados por amigos antes de Mauro
            for i in range(min(picks_before_mauro, len(opciones))):
                results = data_agent.get_player_info(opciones[i])
                if results:
                    draft_agent.mark_as_drafted(results[0]["id"])
                    print(f"  (Simulado: {results[0]['name']} tomado por amigo antes de tu pick)")

            # Marcar el pick de Mauro (opcion despues de los picks de amigos)
            idx_mauro = picks_before_mauro
            if idx_mauro < len(opciones):
                nombre_mauro = opciones[idx_mauro]
                results = data_agent.get_player_info(nombre_mauro)
                if results:
                    draft_agent.add_to_roster(
                        results[0]["id"],
                        results[0]["name"],
                        results[0]["position"]
                    )
                    print(f"  (Simulado: {results[0]['name']} agregado a tu roster)")

            # Marcar jugadores tomados por amigos despues de Mauro
            for i in range(picks_after_mauro):
                idx = idx_mauro + 1 + i
                if idx < len(opciones):
                    results = data_agent.get_player_info(opciones[idx])
                    if results:
                        draft_agent.mark_as_drafted(results[0]["id"])
                        print(f"  (Simulado: {results[0]['name']} tomado por amigo despues de tu pick)")
        else:
            print("\n¡Draft completado! Buena suerte en la temporada. 🏈")
            print("\nROSTER FINAL DE MAURO:")
            for p in draft_agent.my_roster:
                print(f"  {p['position']:4} | {p['name']}")

if __name__ == "__main__":
    run_draft_session()