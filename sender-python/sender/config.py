import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class SenderConfig:
    host: str
    port: int


def parse_args(argv: list[str] | None = None) -> SenderConfig:
    parser = argparse.ArgumentParser(description="Emisor de Redes")
    parser.add_argument("--host", default="127.0.0.1", help="Host del receptor (por defecto 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del receptor (por defecto 5000)")
    args = parser.parse_args(argv)
    if not (1 <= args.port <= 65535):
        parser.error("El puerto debe estar entre 1 y 65535")
    return SenderConfig(host=args.host, port=args.port)
