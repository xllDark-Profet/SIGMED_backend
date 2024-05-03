class SolicitudDTO:
    def __init__(self, id_usuario, direccion, sintomas_presentes, emergencia_detectada, nombre_hospital, triage):
        self.id_usuario = id_usuario
        self.direccion = direccion
        self.sintomas_presentes = sintomas_presentes
        self.emergencia_detectada = emergencia_detectada
        self.nombre_hospital = nombre_hospital
        self.triage = triage
        
class RespuestasDTO:
    def __init__(self, sintomas_presentes):
        self.sintomas_presentes = sintomas_presentes