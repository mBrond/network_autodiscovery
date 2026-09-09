class Device:
    def __init__(self, ip: str, mac: str, fabricante: str = "Desconhecido", tipo: str = "Host"):
        self.ip = ip
        self.mac = mac.lower()
        self.fabricante = fabricante
        self.tipo = tipo
        self.status = 0 
        #-1: off, 
        # 0: on, 
        # >0: RETORNADO (contando iterações para virar ON)

        self._iteracoes_amarelas = 3

    def status_nome(self):
        if self.status == -1:
            return "OFF"
        elif self.status == 0:
            return "ON"
        else:
            return "RETORNADO"

    def marca_offline(self):
        self.status = -1

    def marca_retornado(self):
        if self.status == -1:
            self.status = 3
        elif self.status >0:
            self.status = self.status - 1 
