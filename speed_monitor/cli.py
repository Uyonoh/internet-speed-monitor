import time
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
import pandas as pd
from typing import Optional
import logging

from .speed_tester import SpeedTester
from .storage import DataStorage
from .scheduler import SpeedTestScheduler
from config import config

console = Console()
app = typer.Typer(help="Internet Speed Monitor CLI")

def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

@app.command()
def run(
    immediate: bool = typer.Option(config.IMMEDIATE_TEST, 
                                  help="Run test immediately on startup"),
    interval: int = typer.Option(config.TEST_INTERVAL_MINUTES,
                                help="Test interval in minutes"),
    verbose: bool = typer.Option(False, help="Enable verbose logging")
):
    """
    Start the speed monitor with periodic testing
    """
    setup_logging(verbose)
    
    storage = DataStorage()
    tester = SpeedTester()
    
    def perform_test():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running speed test...", total=None)
            result = tester.run_test()
            progress.update(task, completed=1)
        
        storage.save_result(result)
        
        if result['success']:
            console.print(f"[green]✓ Test completed: {result['download_mbps']} Mbps down, "
                         f"{result['upload_mbps']} Mbps up[/green]")
        else:
            console.print(f"[red]✗ Test failed after {result['attempts']} attempts[/red]")
    
    # Start scheduler
    scheduler = SpeedTestScheduler(perform_test, immediate=immediate, interval=interval)
    
    console.print(Panel.fit(
        f"[bold]Internet Speed Monitor Started[/bold]\n\n"
        f"• Interval: {interval} minutes\n"
        f"• Immediate test: {'Yes' if immediate else 'No'}\n"
        f"• Data file: {config.DATA_FILE}\n"
        f"• Max retries: {config.MAX_RETRIES}",
        title="Status"
    ))
    
    try:
        scheduler.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        scheduler.stop()
        console.print("[green]Monitor stopped[/green]")

@app.command()
def test():
    """
    Run a single speed test immediately
    """
    console.print("Running single speed test...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Testing...", total=None)
        tester = SpeedTester()
        result = tester.get_single_test()
        progress.update(task, completed=1)
    
    if result:
        table = Table(title="Speed Test Results", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Timestamp", result['timestamp'])
        table.add_row("Download", f"{result['download_mbps']} Mbps")
        table.add_row("Upload", f"{result['upload_mbps']} Mbps")
        table.add_row("Ping", f"{result['ping_ms']} ms")
        table.add_row("Server", f"{result['server_name']} ({result['server_country']})")
        
        console.print(table)
        
        # Save result
        storage = DataStorage()
        storage.save_result(result)
        console.print(f"[dim]Result saved to {config.DATA_FILE}[/dim]")

@app.command()
def stats(
    days: Optional[int] = typer.Option(None, help="Filter data from last N days")
):
    """
    Show statistics from collected data
    """
    storage = DataStorage()
    df = storage.load_data()
    
    if df.empty:
        console.print("[yellow]No data available. Run tests first.[/yellow]")
        return
    
    if days:
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        df = df[df['timestamp'] > cutoff]
    
    stats = storage.get_stats()
    
    if not stats:
        console.print("[yellow]No successful tests found in the data.[/yellow]")
        return
    
    # Statistics table
    stats_table = Table(title=f"Speed Test Statistics (Last {days} days)" if days else "Speed Test Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right")
    
    stats_table.add_row("Total Tests", str(stats['total_tests']))
    stats_table.add_row("Successful Tests", str(stats['successful_tests']))
    stats_table.add_row("Success Rate", f"{stats['success_rate']}%")
    stats_table.add_row("Average Download", f"{stats['avg_download']} Mbps")
    stats_table.add_row("Average Upload", f"{stats['avg_upload']} Mbps")
    stats_table.add_row("Average Ping", f"{stats['avg_ping']} ms")
    stats_table.add_row("Max Download", f"{stats['max_download']} Mbps")
    stats_table.add_row("Min Download", f"{stats['min_download']} Mbps")
    stats_table.add_row("Recent (24h)", str(stats['recent_tests']))
    stats_table.add_row("Data Since", stats['data_since'])
    
    console.print(stats_table)
    
    # Recent tests table
    if not df.empty:
        recent_table = Table(title="Recent Tests (5 most recent)")
        recent_table.add_column("Timestamp", style="dim")
        recent_table.add_column("Download", justify="right")
        recent_table.add_column("Upload", justify="right")
        recent_table.add_column("Ping", justify="right")
        recent_table.add_column("Status")
        
        for _, row in df.head(5).iterrows():
            status = "[green]✓[/green]" if row['success'] else "[red]✗[/red]"
            download = f"{row['download_mbps']} Mbps" if row['success'] else "Failed"
            upload = f"{row['upload_mbps']} Mbps" if row['success'] else "Failed"
            ping = f"{row['ping_ms']} ms" if row['success'] else "—"
            
            recent_table.add_row(
                row['timestamp'].strftime('%Y-%m-%d %H:%M'),
                download,
                upload,
                ping,
                status
            )
        
        console.print(recent_table)

@app.command()
def export(
    format: str = typer.Option("csv", help="Export format: csv or json"),
    output: str = typer.Option(None, help="Output file path")
):
    """
    Export collected data to a file
    """
    storage = DataStorage()
    df = storage.load_data()
    
    if df.empty:
        console.print("[yellow]No data to export.[/yellow]")
        return
    
    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"speed_data_export_{timestamp}.{format}"
    
    try:
        if format.lower() == 'csv':
            df.to_csv(output, index=False)
        elif format.lower() == 'json':
            df.to_json(output, orient='records', indent=2)
        else:
            console.print(f"[red]Unsupported format: {format}[/red]")
            return
        
        console.print(f"[green]Data exported to {output} ({len(df)} records)[/green]")
    except Exception as e:
        console.print(f"[red]Export failed: {str(e)}[/red]")

if __name__ == "__main__":
    app()