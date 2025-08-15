#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from scanner import verify_subdomains
from sources import gather_subdomains

app = typer.Typer()
console = Console()

@app.command()
def scan(domain: str,
         method: str = typer.Option("ping", help="Verification method: ping, top10, top100, custom"),
         ports: str = typer.Option("", help="Comma-separated ports if method=custom"),
         concurrency: int = typer.Option(50, help="Number of concurrent checks")):
    """
    Discover and verify subdomains for a given domain.
    """
    console.print(f"[bold green]Gathering subdomains for[/bold green] {domain}...")
    subs = gather_subdomains(domain)

    if not subs:
        console.print("[bold red]No subdomains found[/bold red]")
        raise typer.Exit()

    console.print(f"[bold cyan]{len(subs)}[/bold cyan] candidates found. Verifying...")

    if method == "custom":
        if not ports:
            console.print("[bold red]Custom mode requires --ports[/bold red]")
            raise typer.Exit()
        port_list = [int(p) for p in ports.split(",")]
    elif method == "top10":
        port_list = [80, 443, 22, 21, 25, 53, 445, 3389, 3306, 8080]
    elif method == "top100":
        # Import from utils (top 100 list)
        from utils import TOP_100_PORTS
        port_list = TOP_100_PORTS
    else:
        port_list = []

    results = verify_subdomains(subs, method, port_list, concurrency)

    table = Table(title="Subdomain Scan Results")
    table.add_column("Subdomain", style="cyan")
    table.add_column("Alive?", style="green")
    table.add_column("Open Ports", style="yellow")

    for sub, alive, open_ports in results:
        table.add_row(sub, "✅" if alive else "❌", ", ".join(str(p) for p in open_ports))

    console.print(table)

if __name__ == "__main__":
    app()
