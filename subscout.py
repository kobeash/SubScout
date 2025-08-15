#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from scanner import verify_subdomains
from sources import gather_subdomains
import csv

app = typer.Typer()
console = Console()

@app.command()
def scan(
    domain: str,
    method: str = typer.Option("ping", "-m", "--method", help="Verification method: ping, top10, top100, custom"),
    ports: str = typer.Option("", "-p", "--ports", help="Comma-separated ports if method=custom"),
    concurrency: int = typer.Option(50, "-c", "--concurrency", help="Number of concurrent checks"),
    csv_file: str = typer.Option(None, "-C", "--csv", help="Save results to CSV file"),
    txt_file: str = typer.Option(None, "-T", "--txt", help="Save results to TXT file"),
):
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
        from utils import TOP_100_PORTS
        port_list = TOP_100_PORTS
    else:
        port_list = []

    results = verify_subdomains(subs, method, port_list, concurrency)

    # Display rich table
    table = Table(title="Subdomain Scan Results")
    table.add_column("Subdomain", style="cyan")
    table.add_column("Alive?", style="green")
    table.add_column("Open Ports", style="yellow")

    for sub, alive, open_ports in results:
        table.add_row(sub, "✅" if alive else "❌", ", ".join(str(p) for p in open_ports))

    console.print(table)

    # Export CSV if requested
    if csv_file:
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["subdomain", "alive", "open_ports"])
            writer.writeheader()
            for sub, alive, open_ports in results:
                writer.writerow({
                    "subdomain": sub,
                    "alive": alive,
                    "open_ports": ", ".join(str(p) for p in open_ports)
                })
        console.print(f"[bold blue]Results saved to CSV:[/bold blue] {csv_file}")

    # Export TXT if requested
    if txt_file:
        with open(txt_file, "w") as f:
            for sub, alive, open_ports in results:
                status = "ALIVE" if alive else "DEAD"
                f.write(f"{sub:25} {status} Ports: {', '.join(str(p) for p in open_ports)}\n")
        console.print(f"[bold blue]Results saved to TXT:[/bold blue] {txt_file}")


if __name__ == "__main__":
    try:
        app()
    except typer.Abort:
        console.print("\nTry 'main.py --help' for more information.")
