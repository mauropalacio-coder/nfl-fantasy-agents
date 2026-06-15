from utils.claude_client import ask_claude

class WaiverAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent

    def recommend(self, my_roster, waiver_position, total_teams=4, trigger=None):
        """
        Recomienda 3 opciones de waiver rankeadas.
        my_roster: roster actual de Mauro
        waiver_position: posicion de Mauro en el waiver wire (1 = mayor prioridad)
        total_teams: total de equipos en la liga
        trigger: razon del analisis (lesion, bajo rendimiento, bye week, etc)
        """
        if not my_roster:
            return "No hay jugadores en el roster para analizar."

        # Construir resumen del roster
        roster_text = "Roster actual de Mauro:\n"
        for p in my_roster:
            roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"

        # Obtener jugadores disponibles en waivers usando rankings reales
        available_text = ""
        if self.data_agent.rankings:
            pool = self.data_agent.get_ranked_draft_pool(
                excluded_ids=[p.get("id", "") for p in my_roster]
            )
            available_text = "\nJUGADORES DISPONIBLES EN WAIVERS (por promedio pts reales):\n"
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
        1. Analiza el roster de Mauro y detecta debilidades o necesidades
        2. Considera su posicion en el waiver wire — si tiene baja prioridad,
           no recomendar jugadores obvios que otros tomaran primero
        3. Recomienda 3 opciones realistas segun su posicion en el wire
        4. Para cada opcion indica quien soltar del roster si es necesario
        5. Prioriza jugadores con alto promedio de puntos disponibles

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

        system_prompt = "Eres un experto en NFL fantasy football waivers. Das recomendaciones precisas considerando la posicion en el waiver wire y el roster actual."

        return ask_claude(prompt, system_prompt=system_prompt, max_tokens=1000)