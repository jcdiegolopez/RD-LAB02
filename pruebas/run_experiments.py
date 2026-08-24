#!/usr/bin/env python3
"""Ejecuta pruebas automatizadas de envio/recepcion contra el receptor Java,
variando algoritmo, tamano del mensaje y probabilidad de error por bit.

Reutiliza directamente los modulos del emisor Python (codificacion ASCII,
Hamming SECDED, CRC-32, ruido, protocolo y cliente de socket) para no
duplicar logica ya implementada; solo se evita la interfaz interactiva.

Uso:
    python3 pruebas/run_experiments.py

Requiere: receptor Java compilable con Maven (mvn) y Python 3.11+.
Genera: pruebas/resultados/raw_results.csv
"""
from __future__ import annotations

import csv
import json
import random
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SENDER_ROOT = REPO_ROOT / "sender-python"
RECEIVER_ROOT = REPO_ROOT / "receiver-java"
OUTPUT_DIR = Path(__file__).resolve().parent / "resultados"

HOST = "127.0.0.1"
PORT = 5099  # puerto dedicado para no chocar con una instancia manual en 5000
SEED = 20260823

sys.path.insert(0, str(SENDER_ROOT))
from sender import ascii_codec, client, crc32_codec, hamming_secded, noise, protocol  # noqa: E402

_FIELD_RE = re.compile(r'"([A-Za-z][A-Za-z0-9]*)"\s*:\s*(?:"((?:\\.|[^"\\])*)"|(-?\d+)|null)')
_ESCAPE_MAP = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", '"': '"', "\\": "\\", "/": "/"}


def _unescape(value: str) -> str:
    out = []
    i = 0
    while i < len(value):
        ch = value[i]
        if ch == "\\" and i + 1 < len(value):
            nxt = value[i + 1]
            if nxt in _ESCAPE_MAP:
                out.append(_ESCAPE_MAP[nxt])
                i += 2
                continue
            if nxt == "u" and i + 6 <= len(value):
                out.append(chr(int(value[i + 2:i + 6], 16)))
                i += 6
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def parse_response_lenient(line: str) -> dict:
    """Parsea la respuesta del receptor tolerando JSON inválido.

    El receptor Java solo escapa \\n \\r \\t al reconstruir el mensaje; si el
    ruido corrompe un byte y el carácter decodificado es otro carácter de
    control, produce JSON estrictamente inválido (bug real: el emisor
    Python real crashearía en protocol.parse_response, que no captura
    json.JSONDecodeError). Aquí se recupera vía regex para no perder la
    prueba, y se marca malformed_json=1 para cuantificar el problema.
    """
    try:
        data = json.loads(line)
        return {
            "status": data.get("status"),
            "errors_detected": int(data.get("errorsDetected", 0)),
            "errors_corrected": int(data.get("errorsCorrected", 0)),
            "message": data.get("message"),
            "malformed_json": 0,
        }
    except json.JSONDecodeError:
        fields: dict[str, str] = {}
        for match in _FIELD_RE.finditer(line):
            name = match.group(1)
            if match.group(2) is not None:
                fields[name] = _unescape(match.group(2))
            elif match.group(3) is not None:
                fields[name] = match.group(3)
        return {
            "status": fields.get("status"),
            "errors_detected": int(fields.get("errorsDetected", "0") or 0),
            "errors_corrected": int(fields.get("errorsCorrected", "0") or 0),
            "message": fields.get("message"),
            "malformed_json": 1,
        }

ALGORITHMS = {
    "HAMMING": hamming_secded,
    "CRC32": crc32_codec,
}

SIZES_CHARS = [1, 2, 4, 8, 16, 32, 64, 128]
# Nota: el receptor Java usa un parser JSON basado en regex que sufre
# StackOverflowError con tramas muy largas (frameBits > ~2000 bits); se
# limita el tamaño máximo de prueba para no derribar el proceso.
PROBS = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.08, 0.12, 0.2]
FIXED_SIZE_FOR_PROB_SWEEP = 32
FIXED_PROB_FOR_SIZE_SWEEP = 0.01
TRIALS_PROB_SWEEP = 200
TRIALS_SIZE_SWEEP = 150


def build_message(rng: random.Random, length_chars: int) -> str:
    return "".join(chr(rng.randint(32, 126)) for _ in range(length_chars))


def run_trial(rng: random.Random, experiment: str, algorithm: str, message: str, probability: float) -> dict:
    codec = ALGORITHMS[algorithm]
    original_bits = ascii_codec.encode(message)
    frame_bits = codec.encode(original_bits)
    noisy_bits, flipped = noise.apply_noise(frame_bits, probability, rng)

    request_json = protocol.build_request_json(
        message_id="exp",
        algorithm=algorithm,
        original_bit_length=len(original_bits),
        frame_bits=noisy_bits,
    )
    response_line = client.send_frame(HOST, PORT, request_json)
    response = parse_response_lenient(response_line)

    overhead_bits = len(frame_bits) - len(original_bits)
    return {
        "experiment": experiment,
        "algorithm": algorithm,
        "size_chars": len(message),
        "size_bits": len(original_bits),
        "probability": probability,
        "flipped_bits": flipped,
        "frame_bits_len": len(frame_bits),
        "overhead_bits": overhead_bits,
        "overhead_pct": round(overhead_bits / len(original_bits) * 100, 4),
        "status": response["status"],
        "errors_detected": response["errors_detected"],
        "errors_corrected": response["errors_corrected"],
        "message_correct": int(response["message"] == message),
        "silent_corruption": int(response["status"] in ("OK", "CORRECTED") and response["message"] != message),
        "malformed_json": response["malformed_json"],
    }


def start_receiver():
    log_path = OUTPUT_DIR / "receiver.log"
    log_file = log_path.open("w")
    proc = subprocess.Popen(
        ["mvn", "-q", "exec:java", f"-Dexec.args=--port {PORT}"],
        cwd=RECEIVER_ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 90
    while time.time() < deadline:
        if proc.poll() is not None:
            log_file.close()
            raise RuntimeError(f"El receptor terminó antes de iniciar; revisa {log_path}")
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                return proc, log_file
        except OSError:
            time.sleep(1)
    proc.kill()
    log_file.close()
    raise RuntimeError(f"El receptor no inició a tiempo; revisa {log_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Iniciando receptor Java en {HOST}:{PORT}...")
    proc, log_file = start_receiver()
    print("Receptor listo. Ejecutando pruebas...")

    rng = random.Random(SEED)
    rows: list[dict] = []
    try:
        # Experimento A: overhead determinístico por tamaño (sin ruido, 1 corrida por combinación)
        for algorithm in ALGORITHMS:
            for size in SIZES_CHARS:
                message = build_message(rng, size)
                rows.append(run_trial(rng, "A_overhead", algorithm, message, 0.0))

        # Experimento B: éxito/corrección/detección vs probabilidad de error (tamaño fijo)
        for algorithm in ALGORITHMS:
            for p in PROBS:
                for _ in range(TRIALS_PROB_SWEEP):
                    message = build_message(rng, FIXED_SIZE_FOR_PROB_SWEEP)
                    rows.append(run_trial(rng, "B_vs_probabilidad", algorithm, message, p))

        # Experimento C: éxito vs tamaño del mensaje (probabilidad fija moderada)
        for algorithm in ALGORITHMS:
            for size in SIZES_CHARS:
                for _ in range(TRIALS_SIZE_SWEEP):
                    message = build_message(rng, size)
                    rows.append(run_trial(rng, "C_vs_tamano", algorithm, message, FIXED_PROB_FOR_SIZE_SWEEP))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_file.close()

    out_csv = OUTPUT_DIR / "raw_results.csv"
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} pruebas ejecutadas -> {out_csv}")


if __name__ == "__main__":
    main()
