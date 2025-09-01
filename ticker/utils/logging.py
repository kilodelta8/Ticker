from __future__ import annotations
from rich.console import Console
from datetime import datetime

console = Console()

def info(msg: str):
    console.log(f"[bold cyan]INFO[/]: {msg}")

def warn(msg: str):
    console.log(f"[bold yellow]WARN[/]: {msg}")

def error(msg: str):
    console.log(f"[bold red]ERROR[/]: {msg}")

def banner(title: str):
    console.rule(f"[bold magenta]{title}[/] • {datetime.now().isoformat(timespec='seconds')}")
