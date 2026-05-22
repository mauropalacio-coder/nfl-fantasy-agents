from utils.claude_client import ask_claude

# QBs reservados por jugador en la liga - Temporada 2026
RESERVED_QBS = {
    "Mauro": "Brock Purdy",
    "Amigo1": "Sam Darnold",
    "Amigo2": "Aaron Rodgers",  # PIT - TBD
    "Amigo3": "Drake Maye",
}

# Estructura de roster en NFL Fantasy estandar
ROSTER_SLOTS = {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "FLEX": 1,
    "K": 1,
    "DEF": 1,
    "BENCH": 7,
}

TOTAL_ROUNDS = 15

class DraftAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.my_roster = []
        self.drafted_players = []

    def get_pick_position(self, round_number):
        """
        Draft serpentina - Mauro empieza en pick #3 de 4.
        Rondas impares: pick #3 (penultimo)
        Rondas pares: pick #2 (segundo)
        """
        if round_number % 2 == 1:
            return 3
        else:
            return 2

    def get_next_pick_info(self, round_number):
        """Informa cuantos picks hay hasta el proximo turno de Mauro."""
        current_pos = self.get_pick_position(round_number)
        next_pos = self.get_pick_position(round_number + 1)
        picks_until_next = (4 - current_pos) + next_pos
        return picks_until_next

    def add_to_roster(self, player_id, player_name, position):
        """Agrega un jugador al roster de Mauro."""
        self.my_roster.append({
            "id": player_id,
            "name": player_name,
            "position": position,
        })
        self.drafted_players.append(player_id)

    def mark_as_drafted(self, player_id):
        """Marca un jugador como tomado por otro participante."""
        if player_id not in self.drafted_players:
            self.drafted_players.append(player_id)

    def get_available_players(self):
        """Retorna jugadores que aun no fueron draftados."""
        return {
            pid: info
            for pid, info in self.data_agent.players.items()
            if pid not in self.drafted_players
        }

    def get_roster_needs(self):
        """Analiza que posiciones necesita cubrir el roster."""
        counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "K": 0, "DEF": 0}
        for player in self.my_roster:
            pos = player["position"]
            if pos in counts:
                counts[pos] += 1

        needs = []
        if counts["QB"] == 0:
            needs.append("QB - necesitas tu starter")
        if counts["RB"] < 2:
            needs.append(f"RB - tienes {counts['RB']}/2 starters")
        if counts["WR"] < 2:
            needs.append(f"WR - tienes {counts['WR']}/2 starters")
        if counts["TE"] == 0:
            needs.append("TE - necesitas tu starter")
        if counts["K"] == 0:
            needs.append("K - necesitas tu kicker")
        if counts["DEF"] == 0:
            needs.append("DEF - necesitas tu defensa")

        bench_current = max(0, len(self.my_roster) - sum(counts.values()))
        if bench_current < ROSTER_SLOTS["BENCH"]:
            needs.append(f"BENCH - {bench_current}/{ROSTER_SLOTS['BENCH']} slots cubiertos")

        return needs

    def get_draft_strategy(self, round_number):
        """Define la estrategia de draft segun la ronda actual."""
        if round_number <= 4:
            return """
            ESTRATEGIA RONDAS 1-4 (Elite starters):
            - Prioridad: RB y WR de elite
            - NO tomar QB, K ni DEF todavia
            - Solo considerar TE si es de primer nivel (Kelce, Andrews)
            - Tomar el mejor jugador disponible en posiciones escasas
            """
        elif round_number <= 8:
            return """
            ESTRATEGIA RONDAS 5-8 (Completar starters):
            - Completar los 2 RB starters si aun no los tienes
            - Completar los 2 WR starters si aun no los tienes
            - Tomar TE starter si aun no tienes uno
            - Ronda 7-8 es el momento ideal para tomar a Brock Purdy
            - Evitar K y DEF todavia
            """
        elif round_number <= 11:
            return """
            ESTRATEGIA RONDAS 9-11 (Mejor banca disponible):
            - Cubrir banca con el mejor jugador disponible por posicion
            - Priorizar RB y WR de banca con upside
            - Si aun no tienes QB, tomarlo ahora si o si
            - Considerar TE de banca si hay valor
            """
        else:
            return """
            ESTRATEGIA RONDAS 12-15 (Completar roster):
            - Tomar K y DEF en estas rondas
            - Completar banca con jugadores de upside o handcuffs
            - Priorizar cubrir posiciones de starter que aun falten
            - K y DEF son intercambiables, no gastar picks tempranos en ellos
            """

    def recommend(self, round_number):
        """Genera 5 recomendaciones de draft para la ronda actual."""
        roster_needs = self.get_roster_needs()
        reserved_qbs = list(RESERVED_QBS.values())
        my_qb = RESERVED_QBS["Mauro"]
        pick_position = self.get_pick_position(round_number)
        picks_until_next = self.get_next_pick_info(round_number)
        rounds_remaining = TOTAL_ROUNDS - round_number
        strategy = self.get_draft_strategy(round_number)

        # Roster summary
        roster_summary = "Roster actual de Mauro:\n"
        if self.my_roster:
            for p in self.my_roster:
                roster_summary += f"  - {p['name']} ({p['position']})\n"
        else:
            roster_summary += "  (vacio - primer pick)\n"

        # Jugadores disponibles con datos completos
        draft_pool = self.data_agent.get_draft_pool(excluded_ids=self.drafted_players)

        def format_players(players, limit=15):
            return "\n".join([
                f"  - {p['name']} | {p['team']} | Edad: {p['age']} | Exp: {p['years_exp']} anos"
                for p in players[:limit]
            ])

        prompt = f"""
        Eres el asistente de draft de Mauro en su liga de NFL Fantasy Football 2026.
        Liga de 4 participantes, draft serpentina de {TOTAL_ROUNDS} rondas.

        CONTEXTO DEL DRAFT:
        - Ronda actual: {round_number} de {TOTAL_ROUNDS}
        - Posicion de pick de Mauro esta ronda: #{pick_position} de 4
        - Picks hasta su proximo turno: {picks_until_next} picks
        - Rondas restantes: {rounds_remaining}

        {roster_summary}

        NECESIDADES DEL ROSTER:
        {chr(10).join(roster_needs) if roster_needs else "Roster completo"}

        {strategy}

        REGLA ESPECIAL DE LIGA - QBs reservados:
        - Mauro tomara a: {my_qb} (cuando sea el momento correcto en el draft)
        - NO recomendar estos QBs para Mauro: {', '.join([qb for qb in reserved_qbs if qb != my_qb])}

        JUGADORES DISPONIBLES POR POSICION (ordenados por experiencia):
        QBs:
        {format_players(draft_pool.get('QB', []), 15)}

        RBs:
        {format_players(draft_pool.get('RB', []), 20)}

        WRs:
        {format_players(draft_pool.get('WR', []), 20)}

        TEs:
        {format_players(draft_pool.get('TE', []), 15)}

        Ks:
        {format_players(draft_pool.get('K', []), 10)}

        DEFs:
        {format_players(draft_pool.get('DEF', []), 10)}

        INSTRUCCIONES:
        1. Usa los datos de edad y experiencia para evaluar el valor de cada jugador
        2. Considera cuantos picks hay hasta el proximo turno de Mauro
        3. Evalua si un jugador top puede desaparecer antes de su proximo pick
        4. Sigue la estrategia definida para esta ronda
        5. NO recomendar los QBs reservados para los amigos
        6. Si es momento de tomar a {my_qb} segun la estrategia, incluirlo como opcion
        7. Indica claramente si la recomendacion es para starter o banca

        Dame 5 opciones rankeadas en este formato exacto:

        OPCION 1: [Nombre] | [Posicion] | [Equipo] | [Starter/Bench]
        Razon: [explicacion breve]

        OPCION 2: [Nombre] | [Posicion] | [Equipo] | [Starter/Bench]
        Razon: [explicacion breve]

        OPCION 3: [Nombre] | [Posicion] | [Equipo] | [Starter/Bench]
        Razon: [explicacion breve]

        OPCION 4: [Nombre] | [Posicion] | [Equipo] | [Starter/Bench]
        Razon: [explicacion breve]

        OPCION 5: [Nombre] | [Posicion] | [Equipo] | [Starter/Bench]
        Razon: [explicacion breve]
        """

        system_prompt = "Eres un experto en NFL fantasy football draft strategy. Das recomendaciones precisas adaptadas al contexto del roster, la estrategia por ronda y el draft serpentina."

        recommendation = ask_claude(prompt, system_prompt=system_prompt, max_tokens=1200)
        return recommendation