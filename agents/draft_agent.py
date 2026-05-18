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
    "BENCH": 7,  # 15 total - 8 starters = 7 bench
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
        print(f"Agregado al roster: {player_name} ({position})")

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

    def recommend(self, round_number):
        """Genera 4 recomendaciones de draft para la ronda actual."""
        roster_needs = self.get_roster_needs()
        reserved_qbs = list(RESERVED_QBS.values())
        my_qb = RESERVED_QBS["Mauro"]
        pick_position = self.get_pick_position(round_number)
        picks_until_next = self.get_next_pick_info(round_number)
        rounds_remaining = TOTAL_ROUNDS - round_number

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
        4. Considera las necesidades del roster sin sacrificar valor en rondas tempranas
        5. En rondas tardias (10+) prioriza cubrir starters faltantes y banca util
        6. NO recomendar los QBs reservados para los amigos
        7. Si Mauro aun no tiene QB y {my_qb} esta disponible y es momento correcto, incluirlo

        Dame 4 opciones rankeadas en este formato exacto:

        OPCION 1: [Nombre] | [Posicion] | [Equipo]
        Razon: [explicacion breve]

        OPCION 2: [Nombre] | [Posicion] | [Equipo]
        Razon: [explicacion breve]

        OPCION 3: [Nombre] | [Posicion] | [Equipo]
        Razon: [explicacion breve]

        OPCION 4: [Nombre] | [Posicion] | [Equipo]
        Razon: [explicacion breve]
        """

        system_prompt = "Eres un experto en NFL fantasy football draft strategy. Das recomendaciones precisas y adaptadas al contexto del roster, los datos reales de los jugadores y el draft serpentina."

        recommendation = ask_claude(prompt, system_prompt=system_prompt, max_tokens=1000)
        return recommendation