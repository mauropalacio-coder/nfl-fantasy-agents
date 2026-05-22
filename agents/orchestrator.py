from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent
from agents.weekly_agent import WeeklyAgent
from agents.waiver_agent import WaiverAgent

MODES = {
    "1": "draft",
    "2": "weekly",
    "3": "waiver",
}

class Orchestrator:
    def __init__(self):
        print("Iniciando NFL Fantasy AI Agents...\n")
        self.data_agent = DataAgent()
        self.data_agent.load_data()
        self.draft_agent = DraftAgent(self.data_agent)
        self.weekly_agent = WeeklyAgent(self.data_agent)
        self.waiver_agent = WaiverAgent(self.data_agent)
         # Roster simulado para pruebas - reemplazar con roster real post-draft
        self.my_roster = [
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

    def get_input(self, prompt):
        """Pide input y valida que no este vacio."""
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
        print("4. Salir")
        print("="*50)
        return self.get_input("Selecciona una opcion (1-4): ")

    def show_my_roster(self):
        if not self.my_roster:
            print("\nRoster vacio.")
        else:
            print("\nTU ROSTER ACTUAL:")
            for p in self.my_roster:
                print(f"  {p['position']:4} | {p['name']} | {p['team']}")

    def run_draft_mode(self):
        """Ejecuta el flujo completo de draft."""
        from draft_session import run_draft_session
        run_draft_session()

    def run_weekly_mode(self):
        """Ejecuta el analisis semanal de lineup."""
        print("\n" + "="*50)
        print("   ANALISIS SEMANAL DE LINEUP")
        print("="*50)

        # Verificar roster
        if not self.my_roster:
            print("\nNo tienes jugadores en tu roster.")
            print("Primero ejecuta el modo Draft o carga tu roster.")
            return

        self.show_my_roster()

        # Datos de la semana
        week = self.get_input("\n¿Que semana de la NFL es? (ej: 5): ")
        opponent_name = self.get_input("Nombre del rival: ")

        # Ingresar roster del rival
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

            # Buscar jugador en la base
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
                # Ingresar manualmente si no se encuentra
                team = self.get_input(f"  Equipo de {nombre} (ej: KC): ").upper()
                opponent_roster.append({
                    "name": nombre,
                    "position": pos,
                    "team": team,
                })
                print(f"  ✓ {nombre} | {pos} | {team} (manual)")

            pos_index += 1

        # Generar recomendacion
        print("\nGenerando analisis de lineup...\n")
        recomendacion = self.weekly_agent.recommend_lineup(
            roster=self.my_roster,
            week=int(week),
            opponent_name=opponent_name,
            opponent_roster=opponent_roster,
        )
        print(recomendacion)

    def run_waiver_mode(self):
        """Ejecuta el analisis de waivers."""
        print("\n" + "="*50)
        print("   WAIVER / TRADE AGENT")
        print("="*50)
        print("(Proximamente - siguiente sesion)")

    def run(self):
        """Loop principal del orquestador."""
        while True:
            opcion = self.show_menu()

            if opcion == "1":
                self.run_draft_mode()
            elif opcion == "2":
                self.run_weekly_mode()
            elif opcion == "3":
                self.run_waiver_mode()
            elif opcion == "4":
                print("\n¡Hasta la proxima, Mauro! 🏈")
                break
            else:
                print("Opcion invalida. Intenta de nuevo.")