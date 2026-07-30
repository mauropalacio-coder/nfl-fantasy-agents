from utils.claude_client import ask_claude
from utils.league_roster_manager import get_all_drafted_players

class WaiverAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent

    def recommend(self, my_roster, waiver_position, total_teams=4, trigger=None):
        """
        Recomienda 3 opciones de waiver rankeadas.
        my_roster: roster actual de Mauro (starters + bench)
        waiver_position: posicion de Mauro en el waiver wire
        total_teams: total de equipos en la liga
        trigger: razon del analisis
        """
        if not my_roster:
            return "No hay jugadores en tu roster para analizar."

        # Obtener todos los jugadores apartados en la liga
        all_drafted_ids = get_all_drafted_players()

        # Agregar IDs del roster de Mauro tambien
        my_ids = [p.get("id", "") for p in my_roster]
        all_excluded = list(set(all_drafted_ids + my_ids))

        # Construir resumen del roster de Mauro
        starters = [p for p in my_roster if p.get("slot") == "starter"]
        bench = [p for p in my_roster if p.get("slot") == "bench"]

        if not starters and not bench:
            # Si no tienen slot definido, mostrar todos
            roster_text = "Roster de Mauro:\n"
            for p in my_roster:
                roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"
        else:
            roster_text = "Roster de Mauro:\nTitulares:\n"
            for p in starters:
                roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"
            roster_text += "Banca:\n"
            for p in bench:
                roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"

        # Obtener jugadores disponibles excluyendo todos los apartados
        available_text = ""
        if self.data_agent.rankings:
            pool = self.data_agent.get_ranked_draft_pool(excluded_ids=all_excluded)
            available_text = "\nJUGADORES DISPONIBLES EN WAIVERS (no estan en ningun roster):\n"
            for pos in ["QB", "RB", "WR", "TE", "K", "DEF"]:
                players = pool.get(pos, [])[:8]
                if players:
                    available_text += f"\n{pos}s:\n"
                    for p in players:
                        available_text += f"  - {p['name']} | {p.get('team', 'N/A')} | {p.get('avg_pts', 'N/A')} pts/partido\n"

        trigger_text = f"MOTIVO DEL ANALISIS: {trigger}" if trigger else "ANALISIS GENERAL DE WAIVERS"

        prompt = f"""
        Eres el asistente de waivers de Mauro en su liga de NFL Fantasy Football 2026.
        Liga de 4 participantes.

        {trigger_text}

        POSICION EN EL WAIVER WIRE: #{waiver_position} de {total_teams}
        {"(ALTA PRIORIDAD - puedes ir por los mejores disponibles)" if waiver_position == 1 else ""}
        {"(PRIORIDAD MEDIA - evalua bien antes de usar tu prioridad)" if waiver_position == 2 else ""}
        {"(BAJA PRIORIDAD - evita ir por jugadores obvios que todos quieren)" if waiver_position >= 3 else ""}

        {roster_text}
        {available_text}

        INSTRUCCIONES:
        1. Los jugadores listados como disponibles NO estan en ningun roster de la liga
        2. Analiza el roster de Mauro incluyendo banca — considera si algun suplente
           podria subir al lineup en lugar de buscar en waivers
        3. Considera su posicion en el waiver wire
        4. Recomienda 3 opciones realistas segun su posicion en el wire
        5. Para cada opcion indica quien soltar del roster si es necesario
        6. Prioriza jugadores con alto promedio de puntos disponibles

        Dame 3 opciones en este formato exacto:

        OPCION 1: [Jugador a agregar] | [Posicion] | [Equipo] | [avg pts/partido]
        Soltar: [Jugador a soltar o "Nadie si hay espacio"]
        Razon: [explicacion breve considerando posicion en el wire]

        OPCION 2: [Jugador a agregar] | [Posicion] | [Equipo] | [avg pts/partido]
        Soltar: [Jugador a soltar o "Nadie si hay espacio"]
        Razon: [explicacion breve considerando posicion en el wire]

        OPCION 3: [Jugador a agregar] | [Posicion] | [Equipo] | [avg pts/partido]
        Soltar: [Jugador a soltar o "Nadie si hay espacio"]
        Razon: [explicacion breve considerando posicion en el wire]
        """

        system_prompt = "Eres un experto en NFL fantasy football waivers. Das recomendaciones precisas considerando la posicion en el waiver wire, el roster completo incluyendo banca, y solo jugadores realmente disponibles."

        return ask_claude(prompt, system_prompt=system_prompt, max_tokens=1000)