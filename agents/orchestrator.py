from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent
from agents.weekly_agent import WeeklyAgent
from agents.waiver_agent import WaiverAgent
from utils.roster_manager import load_roster, save_roster, add_player, remove_player, show_roster

class Orchestrator:
    def __init__(self):
        print("Iniciando NFL Fantasy AI Agents...\n")
        self.data_agent = DataAgent()
        self.data_agent.load_data()
        self.data_agent.load_player_rankings(seasons=[2023, 2024, 2025])
        self.draft_agent = DraftAgent(self.data_agent)
        self.weekly_agent = WeeklyAgent(self.data_agent)
        self.waiver_agent = WaiverAgent(self.data_agent)

        # Cargar roster desde archivo persistente
        self.my_roster = load_roster()
        if self.my_roster:
            print(f"Roster cargado: {len(self.my_roster)} jugadores.")
        else:
            print("Roster vacio. Ve a 'Gestionar Roster' para agregar jugadores.")

    def get_input(self, prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Debes ingresar algo. Intenta de nuevo.")

    def show_menu(self):
        print("\n" + "="*50)
        print("   NFL FANTASY AI AGENTS - MENU PRINCIPAL")
        print("="*50)
        print("1. Modo Draft")
        print("2. Analisis Semanal de Lineup")
        print("3. Waiver / Trade")
        print("4. Gestionar Mi Roster")
        print("5. Salir")
        print("="*50)
        return self.get_input("Selecciona una opcion (1-5): ")

    def show_my_roster(self):
        if not self.my_roster:
            print("\nRoster vacio.")
        else:
            print(f"\nTU ROSTER ACTUAL ({len(self.my_roster)} jugadores):")
            for p in sorted(self.my_roster, key=lambda x: x["position"]):
                print(f"  {p['position']:4} | {p['name']:25} | {p['team']}")

    def run_draft_mode(self):
        from draft_session import run_draft_session
        run_draft_session(data_agent=self.data_agent)

    def run_weekly_mode(self):
        print("\n" + "="*50)
        print("   ANALISIS SEMANAL DE LINEUP")
        print("="*50)

        if not self.my_roster:
            print("\nNo tienes jugadores en tu roster.")
            print("Ve a 'Gestionar Mi Roster' para agregar jugadores.")
            return

        self.show_my_roster()

        week = self.get_input("\n¿Que semana de la NFL es? (ej: 5): ")
        opponent_name = self.get_input("Nombre del rival: ")

        print(f"\nIngresa los jugadores titulares de {opponent_name}.")
        print("Escribe 'listo' cuando termines.\n")

        opponent_roster = []
        positions = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"]
        pos_index = 0

        while pos_index < len(positions):
            pos = positions[pos_index]
            nombre = self.get_input(f"  {pos}: ")

            if nombre.lower() == "listo":
                break

            results = self.data_agent.get_player_info(nombre)
            if results:
                player = results[0]
                opponent_roster.append({
                    "name": player["name"],
                    "position": player["position"],
                    "team": player["team"],
                })
                print(f"  ✓ {player['name']} | {player['position']} | {player['team']}")
            else:
                team = self.get_input(f"  Equipo de {nombre} (ej: KC): ").upper()
                opponent_roster.append({
                    "name": nombre,
                    "position": pos,
                    "team": team,
                })
                print(f"  ✓ {nombre} | {pos} | {team} (manual)")

            pos_index += 1

        print("\nGenerando analisis de lineup...\n")
        recomendacion = self.weekly_agent.recommend_lineup(
            roster=self.my_roster,
            week=int(week),
            opponent_name=opponent_name,
            opponent_roster=opponent_roster,
        )
        print(recomendacion)

    def run_waiver_mode(self):
        print("\n" + "="*50)
        print("   WAIVER / TRADE AGENT")
        print("="*50)

        self.show_my_roster()

        if not self.my_roster:
            print("\nNo tienes jugadores en tu roster.")
            return

        waiver_pos = self.get_input("\n¿Cual es tu posicion en el waiver wire? (1-4): ")
        trigger = self.get_input("¿Cual es el motivo? (ej: lesion de CMC, bye week, bajo rendimiento): ")

        print("\nGenerando recomendaciones de waiver...\n")

        recomendacion = self.waiver_agent.recommend(
            my_roster=self.my_roster,
            waiver_position=int(waiver_pos),
            total_teams=4,
            trigger=trigger
        )
        print(recomendacion)

    def run_roster_mode(self):
        """Gestiona el roster de Mauro."""
        while True:
            print("\n" + "="*50)
            print("   GESTIONAR MI ROSTER")
            print("="*50)
            self.show_my_roster()
            print("\n1. Agregar jugador")
            print("2. Eliminar jugador")
            print("3. Volver al menu principal")
            print("="*50)

            opcion = self.get_input("Selecciona una opcion (1-3): ")

            if opcion == "1":
                nombre = self.get_input("Nombre del jugador: ")

                # Buscar en la base de datos
                results = self.data_agent.get_player_info(nombre)
                if results:
                    player = results[0]
                    print(f"  Encontrado: {player['name']} | {player['position']} | {player['team']}")
                    confirmar = self.get_input("¿Agregar al roster? (s/n): ")
                    if confirmar.lower() == "s":
                        self.my_roster = add_player(
                            name=player["name"],
                            position=player["position"],
                            team=player["team"],
                            age=player.get("age"),
                            years_exp=player.get("years_exp"),
                            player_id=player["id"]
                        )
                        print(f"✓ {player['name']} agregado al roster.")
                else:
                    print(f"Jugador no encontrado en la base. Ingresa manualmente:")
                    position = self.get_input("Posicion (QB/RB/WR/TE/K/DEF): ").upper()
                    team = self.get_input("Equipo (ej: SF): ").upper()
                    self.my_roster = add_player(
                        name=nombre,
                        position=position,
                        team=team,
                    )
                    print(f"✓ {nombre} agregado manualmente.")

            elif opcion == "2":
                nombre = self.get_input("Nombre del jugador a eliminar: ")
                self.my_roster = remove_player(nombre)

            elif opcion == "3":
                break

    def run(self):
        while True:
            opcion = self.show_menu()

            if opcion == "1":
                self.run_draft_mode()
            elif opcion == "2":
                self.run_weekly_mode()
            elif opcion == "3":
                self.run_waiver_mode()
            elif opcion == "4":
                self.run_roster_mode()
            elif opcion == "5":
                print("\n¡Hasta la proxima, Mauro! 🏈")
                break
            else:
                print("Opcion invalida. Intenta de nuevo.")