#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEADLOCK - Card Creator & Deck Manager Server
Servidor web local para gestionar, crear e imprimir cartas de Deadlock en tiempo real.
"""

import os
import sys
import json
import csv
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import subprocess

# Asegurar UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PORT = 8080
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HUMAN_CSV = DATA_DIR / "cards_humanos.csv"
OVERLORD_CSV = DATA_DIR / "cards_overlord.csv"
SIMULATION_SCRIPT = BASE_DIR / "simulations" / "balance_model.py"

def read_csv_cards(file_path: Path):
    if not file_path.exists():
        return []
    cards = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cards.append(dict(row))
    return cards

def write_csv_cards(file_path: Path, cards: list, fieldnames: list):
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in cards:
            writer.writerow(c)

class DeadlockHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).resolve().parent), **kwargs)

    def do_GET(self):
        if self.path == "/api/cards":
            human_cards = read_csv_cards(HUMAN_CSV)
            overlord_cards = read_csv_cards(OVERLORD_CSV)
            response_data = {
                "human_cards": human_cards,
                "overlord_cards": overlord_cards
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/simulate":
            try:
                proc = subprocess.run([sys.executable, str(SIMULATION_SCRIPT)], capture_output=True, text=True, encoding="utf-8", errors="replace")
                output = proc.stdout or proc.stderr
            except Exception as e:
                output = f"Error al ejecutar simulacion: {e}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"output": output}, ensure_ascii=False).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/cards/human":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            card = json.loads(post_body.decode('utf-8'))

            cards = read_csv_cards(HUMAN_CSV)
            # Auto ID si no viene
            if not card.get("id"):
                card["id"] = f"H{len(cards)+1:02d}"
            cards.append(card)
            fieldnames = ["id", "nombre", "tipo", "costo_madera", "costo_piedra", "costo_comida", "costo_medicina", "costo_ap", "efecto", "descripcion", "cantidad_mazo"]
            write_csv_cards(HUMAN_CSV, cards, fieldnames)

            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "card": card}, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/api/cards/overlord":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            card = json.loads(post_body.decode('utf-8'))

            cards = read_csv_cards(OVERLORD_CSV)
            if not card.get("id"):
                card["id"] = f"O{len(cards)+1:02d}"
            cards.append(card)
            fieldnames = ["id", "nombre", "tipo", "costo_ap", "efecto", "requisito_superacion", "descripcion", "cantidad_mazo"]
            write_csv_cards(OVERLORD_CSV, cards, fieldnames)

            self.send_response(201)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "card": card}, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DeadlockHandler)
    url = f"http://localhost:{PORT}"
    print(f"==================================================")
    print(f"🃏 DEADLOCK CARD MANAGER APP INICIADA")
    print(f"🌐 Accede en tu navegador: {url}")
    print(f"==================================================")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")

if __name__ == "__main__":
    run_server()
