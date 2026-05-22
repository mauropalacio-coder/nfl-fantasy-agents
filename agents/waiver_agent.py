from utils.claude_client import ask_claude

class WaiverAgent:
    def __init__(self, data_agent):
        self.data_agent = data_agent

    def recommend(self, my_roster, waiver_position, trigger=None):
        """
        Recomienda 3 opciones de waiver rankeadas.
        my_roster: roster actual de Mauro
        waiver_position: posicion de Mauro en el waiver wire (1 = mayor prioridad)
        trigger: razon del analisis (lesion, bajo rendimiento, bye week, etc)
        """
        print("(Waiver Agent - proximamente)")
        return "Waiver Agent en construccion."