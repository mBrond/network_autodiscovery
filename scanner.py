import time
from oui import get_fabricante, load_oui
from scapy.all import Ether, ARP, srp, conf, get_working_ifaces
from device import Device

class Scanner:
    def __init__(self, ip_rede: str = None, modo_iface: str = 'real'):
        self.ip_rede = ip_rede
        self.modo_iface = modo_iface
        self.interface = self._selecionar_interface()
        self.historico_dispositivos: dict[str, Device] = {}
        self.oui_db = load_oui()
        self.gateway = self.get_gateway()

    def _selecionar_interface(self):
        """Seleciona a interface de rede física descartando interfaces virtuais."""
        if self.modo_iface != 'real' and self.modo_iface is not None:
            return self.modo_iface

        for iface in get_working_ifaces():
            nome_desc = iface.description.lower() if hasattr(iface, 'description') else ""
            if "radmin" in nome_desc or "virtual" in nome_desc or "vbox" in nome_desc:
                continue
            if hasattr(iface, 'ip') and iface.ip and not iface.ip.startswith("127."):
                return iface

        return conf.iface

    def scan(self) -> list[Device]:
        """Procura todos os dispositivos na rede e retorna uma lista de Device com ip/mac."""
        if not self.ip_rede:
            raise ValueError("Endereço/máscara da sub-rede não configurado")

        conf.iface = self.interface

        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp = ARP(pdst=self.ip_rede)
        pacote = ether / arp

        respostas, _ = srp(pacote, timeout=5, verbose=False)

        dispositivos = []
        for _, resposta in respostas:
            ip = resposta.psrc
            mac = resposta.hwsrc.lower()
            tipo = "Router" if ip == self.gateway else "Host"
            novo_dispositivo = Device(ip=ip, mac=mac, fabricante=get_fabricante(mac, self.oui_db), tipo=tipo)
            dispositivos.append(novo_dispositivo)

        return dispositivos

    def gerencia_devices(self, lista_devices: list[Device]):
        """Atualiza o histórico e os estados dos dispositivos a cada iteração."""
        macs_encontrados = {dev.mac: dev for dev in lista_devices}

        macs_atuais = set(macs_encontrados.keys())
        macs_historico = set(self.historico_dispositivos.keys())

        # 1. Atualiza dispositivos que RESPONDERAM no scan atual
        for mac in macs_atuais:
            dev_atual = macs_encontrados[mac]
            
            if mac in self.historico_dispositivos:
                dev_hist = self.historico_dispositivos[mac]
                dev_hist.ip = dev_atual.ip  # Atualiza caso o IP tenha mudado via DHCP
                
                # Alerta se o dispositivo estava OFF e agora voltou
                if dev_hist.status == -1:
                    print(f"[^] DISPOSITIVO RECONECTADO: IP {dev_hist.ip} | MAC {dev_hist.mac}")
                
                dev_hist.marca_retornado()
            else:
                # Novo dispositivo na rede
                print(f"[+] NOVO DISPOSITIVO: IP {dev_atual.ip} | MAC {dev_atual.mac}")
                dev_atual.status = 0  # Inicia como ON estavel
                self.historico_dispositivos[mac] = dev_atual

        # 2. Atualiza dispositivos do histórico que NÃO RESPONDERAM
        macs_ausentes = macs_historico - macs_atuais
        for mac in macs_ausentes:
            dev_hist = self.historico_dispositivos[mac]
            if dev_hist.status != -1:
                print(f"[-] DISPOSITIVO OFFLINE: IP {dev_hist.ip} | MAC {dev_hist.mac}")
            dev_hist.marca_offline()

    def scan_interminente(self, tempo_espera: int = 4):
        """Executa a varredura contínua e reporta entradas/saídas de dispositivos."""
        print(f"[*] Iniciando monitoramento contínuo em {self.ip_rede} (Intervalo: {tempo_espera}s)\n")
        
        try:
            while True:
                inicio_scan = time.time()
                
                encontrados_lista = self.scan()
                self.gerencia_devices(encontrados_lista)

                self._imprimir_relatorio()

                tempo_decorrido = time.time() - inicio_scan
                espera_real = max(0.0, tempo_espera - tempo_decorrido)
                time.sleep(espera_real)

        except KeyboardInterrupt:
            print("fim")

    def _imprimir_relatorio(self):
        print("\n" + "="*120)
        print(f" {'TIPO':<9} | {'IP':<16} | {'MAC':<18} | {'STATUS':<12} | {'FABRICANTE':<30} | {'HORA DA DESCOBERTA':<18}")
        print("="*120)
        for dev in self.historico_dispositivos.values():
            print(f"{dev.tipo:<9} | {dev.ip:<16} | {dev.mac:<18} | {dev.status_nome():<12} | {dev.fabricante:<30} | {dev.descoberta.strftime('%H:%M:%S'):<18}")
        print("="*120 + "\n")

    def get_gateway(self) -> str:
        """Retorna o IP do gateway padrão da interface selecionada."""
        _, _, gateway = conf.route.route("0.0.0.0")
        return gateway