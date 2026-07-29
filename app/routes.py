from flask import Blueprint, render_template, request, jsonify, session
from agents.data_agent import DataAgent
from agents.draft_agent import DraftAgent
from agents.weekly_agent import WeeklyAgent
from agents.waiver_agent import WaiverAgent
from utils.roster_manager import load_roster, add_player, remove_player

main = Blueprint("main", __name__)

# Inicializar agentes una sola vez
print("Iniciando agentes...")
data_agent = DataAgent()
data_agent.load_data()
data_agent.load_player_rankings(seasons=[2023, 2024, 2025])
weekly_agent = WeeklyAgent(data_agent)
waiver_agent = WaiverAgent(data_agent)
print("Agentes listos.")

# Draft agent global con estado
draft_agent = DraftAgent(data_agent)

@main.route("/")
def index():
    roster = load_roster()
    return render_template("index.html", roster=roster)

@main.route("/draft")
def draft():
    return render_template("draft.html")

@main.route("/api/draft/recommend", methods=["POST"])
def draft_recommend():
    data = request.json
    round_number = data.get("round", 1)
    recommendation = draft_agent.recommend(round_number=round_number)

    # Extraer y marcar jugadores tomados automaticamente
    opciones = []
    for linea in recommendation.split("\n"):
        linea_norm = linea.strip().replace("**", "").replace("Ó", "O").replace("ó", "o")
        if linea_norm.upper().startswith("OPCION") and "|" in linea_norm:
            partes = linea_norm.split("|")
            if len(partes) >= 2:
                nombre = partes[0].split(":")[-1].strip()
                if nombre:
                    opciones.append(nombre)

    return jsonify({
        "recommendation": recommendation,
        "round": round_number,
        "opciones": opciones
    })

@main.route("/api/draft/confirm_pick", methods=["POST"])
def draft_confirm_pick():
    """Confirma los picks de la ronda y actualiza el estado del draft."""
    data = request.json
    round_number = data.get("round", 1)
    opciones = data.get("opciones", [])

    pick_position = draft_agent.get_pick_position(round_number)
    picks_before = pick_position - 1
    picks_after = 4 - pick_position

    # Marcar jugadores tomados antes de Mauro
    for i in range(min(picks_before, len(opciones))):
        results = data_agent.get_player_info(opciones[i])
        if results:
            draft_agent.mark_as_drafted(results[0]["id"])

    # Marcar pick de Mauro
    idx_mauro = picks_before
    if idx_mauro < len(opciones):
        results = data_agent.get_player_info(opciones[idx_mauro])
        if results:
            draft_agent.add_to_roster(
                results[0]["id"],
                results[0]["name"],
                results[0]["position"]
            )

    # Marcar jugadores tomados despues de Mauro
    for i in range(picks_after):
        idx = idx_mauro + 1 + i
        if idx < len(opciones):
            results = data_agent.get_player_info(opciones[idx])
            if results:
                draft_agent.mark_as_drafted(results[0]["id"])

    return jsonify({
        "success": True,
        "drafted_count": len(draft_agent.drafted_players),
        "roster": draft_agent.my_roster
    })

@main.route("/api/draft/reset", methods=["POST"])
def draft_reset():
    draft_agent.my_roster = []
    draft_agent.drafted_players = []
    return jsonify({"success": True})

@main.route("/weekly")
def weekly():
    roster = load_roster()
    return render_template("weekly.html", roster=roster)

@main.route("/api/weekly/analyze", methods=["POST"])
def weekly_analyze():
    data = request.json
    week = data.get("week")
    opponent_name = data.get("opponent_name")
    opponent_roster = data.get("opponent_roster", [])

    roster = load_roster()
    if not roster:
        return jsonify({"error": "No tienes jugadores en tu roster."})

    recommendation = weekly_agent.recommend_lineup(
        roster=roster,
        week=int(week),
        opponent_name=opponent_name,
        opponent_roster=opponent_roster,
    )
    return jsonify({"recommendation": recommendation})

@main.route("/waiver")
def waiver():
    roster = load_roster()
    return render_template("waiver.html", roster=roster)

@main.route("/api/waiver/analyze", methods=["POST"])
def waiver_analyze():
    data = request.json
    waiver_position = data.get("waiver_position", 3)
    trigger = data.get("trigger", "")

    roster = load_roster()
    if not roster:
        return jsonify({"error": "No tienes jugadores en tu roster."})

    recommendation = waiver_agent.recommend(
        my_roster=roster,
        waiver_position=int(waiver_position),
        total_teams=4,
        trigger=trigger
    )
    return jsonify({"recommendation": recommendation})

@main.route("/roster")
def roster():
    players = load_roster()
    return render_template("roster.html", roster=players)

@main.route("/api/roster/add", methods=["POST"])
def roster_add():
    data = request.json
    name = data.get("name")
    results = data_agent.get_player_info(name)
    if results:
        player = results[0]
        add_player(
            name=player["name"],
            position=player["position"],
            team=player["team"],
            age=player.get("age"),
            years_exp=player.get("years_exp"),
            player_id=player["id"]
        )
        return jsonify({"success": True, "player": player})
    return jsonify({"success": False, "message": f"Jugador '{name}' no encontrado."})

@main.route("/api/roster/remove", methods=["POST"])
def roster_remove():
    data = request.json
    name = data.get("name")
    remove_player(name)
    return jsonify({"success": True})