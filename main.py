from scanner import Scanner

if __name__ == "__main__":
    REDE_ALVO = "192.168.15.0/24"
    
    scanner = Scanner(ip_rede=REDE_ALVO)

    print(f"Varrendo {scanner.ip_rede}...\n")
    
    scanner.scan_interminente(1) 
