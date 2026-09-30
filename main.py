from snmp_scanner.scanner import Scanner
import sys

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Rode com: python main.py <REDE/MASCARA> <INTERVALO>")
        sys.exit(1)
    
    REDE_ALVO = sys.argv[1]
    INTERVALO = int(sys.argv[2])

    
    scanner = Scanner(ip_rede=REDE_ALVO)

    print(f"Varrendo {scanner.ip_rede}...\n")
    
    scanner.scan_interminente(INTERVALO) 
