from rich.console import Console
from rich.prompt import Prompt

from sender import ascii_codec, noise
from sender.protocol import FrameResponse

console = Console()

_ALGORITHM_CHOICES = ["HAMMING", "CRC32"]

_STATUS_STYLES = {
    "OK": "bold green",
    "CORRECTED": "bold yellow",
    "ERROR_DETECTED": "bold red",
}


def banner(host: str, port: int) -> None:
    console.print("[bold cyan]Emisor de Redes[/bold cyan]")
    console.print(f"Conectará a [green]{host}:{port}[/green]\n")


def ask_message() -> str:
    while True:
        text = Prompt.ask("Mensaje a enviar (ASCII)")
        if not text:
            console.print("[red]El mensaje no puede estar vacío[/red]")
            continue
        try:
            ascii_codec.encode(text)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            continue
        return text


def ask_algorithm() -> str:
    return Prompt.ask("Algoritmo", choices=_ALGORITHM_CHOICES, default="HAMMING")


def ask_noise_probability() -> float:
    while True:
        text = Prompt.ask("Probabilidad de error por bit (formato 1/N)", default="1/1000")
        try:
            return noise.parse_noise_probability(text)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")


def show_frame_summary(algorithm: str, original_bits: str, frame_bits: str,
                        noisy_frame_bits: str, flipped: int) -> None:
    overhead = len(frame_bits) - len(original_bits)
    console.print(f"\n[bold]Algoritmo:[/bold] {algorithm}")
    console.print(f"[bold]Bits originales:[/bold] {len(original_bits)}")
    console.print(f"[bold]Bits de trama (con redundancia):[/bold] {len(frame_bits)} (overhead {overhead})")
    console.print(f"[bold]Bits alterados por ruido:[/bold] {flipped}")
    console.print(f"[dim]Trama enviada: {noisy_frame_bits}[/dim]\n")


def show_response(response: FrameResponse) -> None:
    style = _STATUS_STYLES.get(response.status, "bold red")
    console.print(f"[{style}]{response.status}[/{style}] "
                  f"| detectados: {response.errors_detected} | corregidos: {response.errors_corrected}")
    if response.message is not None:
        console.print(f"[white]Mensaje recuperado:[/white] {response.message}")
    if response.error is not None:
        console.print(f"[red]Detalle:[/red] {response.error}")


def show_connection_error(message: str) -> None:
    console.print(f"[bold red]No se pudo comunicar con el receptor:[/bold red] {message}")
