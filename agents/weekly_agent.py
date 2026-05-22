from utils.claude_client import ask_claude, ask_claude_with_image

# Slots de titulares en NFL Fantasy estandar
STARTER_SLOTS = {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "FLEX": 1,
    "K": 1,
    "DEF": 1,
}

class WeeklyAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent

    def extract_roster_from_image(self, image_path):
        """Extrae el roster del rival desde un screenshot de la app."""
        prompt = """
        Esta es una captura de pantalla de la app NFL Fantasy Football.
        Extrae todos los jugadores que ves en el lineup del equipo rival.
        
        Para cada jugador indica:
        - Nombre completo
        - Posicion (QB, RB, WR, TE, K, DEF)
        - Equipo NFL
        - Si es titular o esta en bench
        
        Responde SOLO en este formato JSON exacto, sin texto adicional:
        {
            "starters": [
                {"name": "Nombre", "position": "POS", "team": "TEAM"},
                ...
            ],
            "bench": [
                {"name": "Nombre", "position": "POS", "team": "TEAM"},
                ...
            ]
        }
        """
        system_prompt = "Eres un experto en NFL Fantasy Football. Extraes informacion precisa de screenshots de la app NFL Fantasy."
        
        result = ask_claude_with_image(
            prompt=prompt,
            image_path=image_path,
            system_prompt=system_prompt,
            max_tokens=1000
        )
        
        # Parsear el JSON
        import json
        try:
            # Limpiar posible markdown
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except Exception as e:
            print(f"Error parseando roster del rival: {e}")
            print(f"Respuesta raw: {result}")
            return {"starters": [], "bench": []}

    def recommend_lineup(self, roster, week, opponent_name=None, opponent_image_path=None):
        """
        Recomienda el lineup optimo para la semana.
        roster: lista de jugadores del roster de Mauro
        week: numero de semana NFL
        opponent_name: nombre del rival
        opponent_image_path: path al screenshot del lineup del rival
        """
        if not roster:
            return "No hay jugadores en el roster para analizar."

        # Extraer roster del rival si hay imagen
        opponent_roster_text = ""
        if opponent_image_path:
            print("Analizando lineup del rival desde screenshot...")
            opponent_data = self.extract_roster_from_image(opponent_image_path)
            
            if opponent_data["starters"]:
                opponent_roster_text = "\nLINEUP DEL RIVAL:\nTitulares:\n"
                for p in opponent_data["starters"]:
                    opponent_roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"
                if opponent_data["bench"]:
                    opponent_roster_text += "Bench:\n"
                    for p in opponent_data["bench"]:
                        opponent_roster_text += f"  - {p['name']} | {p['position']} | {p['team']}\n"
            else:
                opponent_roster_text = "\nNo se pudo extraer el lineup del rival del screenshot."
        elif opponent_name:
            opponent_roster_text = f"\nRival de la semana: {opponent_name} (sin datos de su lineup)"

        # Agrupar roster de Mauro por posicion
        by_position = {}
        for player in roster:
            pos = player["position"]
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)

        def format_position(players):
            return "\n".join([
                f"  - {p['name']} | {p['team']} | Edad: {p.get('age', 'N/A')} | Exp: {p.get('years_exp', 'N/A')} anos"
                for p in players
            ])

        roster_text = ""
        for pos in ["QB", "RB", "WR", "TE", "K", "DEF"]:
            players = by_position.get(pos, [])
            if players:
                roster_text += f"\n{pos}s:\n{format_position(players)}\n"

        prompt = f"""
        Eres el asistente semanal de Mauro en su liga de NFL Fantasy Football 2026.
        Liga de 4 participantes.

        CONTEXTO:
        - Semana NFL: {week}
        - Rival: {opponent_name or 'No especificado'}
        {opponent_roster_text}

        ROSTER DE MAURO:
        {roster_text}

        SLOTS DE TITULARES DISPONIBLES:
        - 1 QB
        - 2 RB
        - 2 WR
        - 1 TE
        - 1 FLEX (RB, WR o TE)
        - 1 K
        - 1 DEF

        INSTRUCCIONES:
        1. Analiza cada jugador considerando edad, experiencia y equipo
        2. Si tienes el lineup del rival, considera sus fortalezas y debilidades
        3. Recomienda el lineup optimo de 8 titulares para esta semana
        4. Indica quien va al bench y por que
        5. Si hay dudas de lesion o rendimiento mencionalas
        6. Sugiere el jugador FLEX mas conveniente
        7. Da un veredicto final del lineup

        Formato de respuesta:

        LINEUP RECOMENDADO:
        QB: [nombre] | [equipo]
        RB1: [nombre] | [equipo]
        RB2: [nombre] | [equipo]
        WR1: [nombre] | [equipo]
        WR2: [nombre] | [equipo]
        TE: [nombre] | [equipo]
        FLEX: [nombre] | [equipo] | [posicion]
        K: [nombre] | [equipo]
        DEF: [nombre] | [equipo]

        BENCH:
        [lista de jugadores en banca con razon breve]

        ANALISIS:
        [razones de las decisiones mas importantes, incluyendo analisis del rival si aplica]
        """

        system_prompt = "Eres un experto en NFL fantasy football. Das recomendaciones de lineup precisas considerando matchups, lesiones, tendencias de temporada y el roster del rival."

        return ask_claude(prompt, system_prompt=system_prompt, max_tokens=1500)