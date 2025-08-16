#!/usr/bin/env python3
"""
Alignator - Political Alignment Analysis
Main application entry point
"""

import os
import sys
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.congress_client import CongressClient
from analysis.alignment_analyzer import AlignmentAnalyzer
from data.data_manager import DataManager
from utils.config import Config

# Load environment variables
load_dotenv()

console = Console()

@click.group()
def cli():
    """Alignator - Political Alignment Analysis Tool"""
    pass

@cli.command()
@click.option('--congress', default=118, help='Congress number (default: 118)')
@click.option('--chamber', default='both', type=click.Choice(['house', 'senate', 'both']), help='Chamber to analyze')
def fetch_members(congress, chamber):
    """Fetch member information from Congress.gov API"""
    console.print(f"[bold blue]Fetching members for Congress {congress}, Chamber: {chamber}[/bold blue]")
    
    try:
        client = CongressClient()
        data_manager = DataManager()
        
        with Progress() as progress:
            task = progress.add_task("Fetching members...", total=None)
            
            members = client.get_members(congress=congress, chamber=chamber)
            data_manager.save_members(members)
            
            progress.update(task, completed=True)
        
        console.print(f"[green]Successfully fetched {len(members)} members[/green]")
        
    except Exception as e:
        console.print(f"[red]Error fetching members: {e}[/red]")

@cli.command()
@click.option('--congress', default=118, help='Congress number (default: 118)')
@click.option('--limit', default=100, help='Number of bills to fetch (default: 100)')
def fetch_bills(congress, limit):
    """Fetch bill information from Congress.gov API"""
    console.print(f"[bold blue]Fetching bills for Congress {congress} (limit: {limit})[/bold blue]")
    
    try:
        client = CongressClient()
        data_manager = DataManager()
        
        with Progress() as progress:
            task = progress.add_task("Fetching bills...", total=limit)
            
            bills = client.get_bills(congress=congress, limit=limit)
            data_manager.save_bills(bills)
            
            progress.update(task, completed=len(bills))
        
        console.print(f"[green]Successfully fetched {len(bills)} bills[/green]")
        
    except Exception as e:
        console.print(f"[red]Error fetching bills: {e}[/red]")

@cli.command()
@click.option('--member-id', help='Specific member ID to analyze')
@click.option('--congress', default=118, help='Congress number (default: 118)')
def analyze_alignment(member_id, congress):
    """Analyze political alignment for members"""
    console.print("[bold blue]Analyzing political alignment...[/bold blue]")
    
    try:
        analyzer = AlignmentAnalyzer()
        data_manager = DataManager()
        
        if member_id:
            # Analyze specific member
            alignment = analyzer.analyze_member(member_id, congress)
            console.print(f"[green]Analysis complete for member {member_id}[/green]")
        else:
            # Analyze all members
            members = data_manager.get_members(congress)
            
            with Progress() as progress:
                task = progress.add_task("Analyzing members...", total=len(members))
                
                for member in members:
                    analyzer.analyze_member(member['id'], congress)
                    progress.advance(task)
            
            console.print(f"[green]Analysis complete for {len(members)} members[/green]")
            
    except Exception as e:
        console.print(f"[red]Error analyzing alignment: {e}[/red]")

@cli.command()
def dashboard():
    """Launch the interactive dashboard"""
    console.print("[bold blue]Launching dashboard...[/bold blue]")
    
    try:
        import streamlit.web.cli as stcli
        import sys
        
        # Set up streamlit arguments
        sys.argv = ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501"]
        sys.exit(stcli.main())
        
    except ImportError:
        console.print("[red]Streamlit not installed. Install with: pip install streamlit[/red]")
    except Exception as e:
        console.print(f"[red]Error launching dashboard: {e}[/red]")

@cli.command()
def status():
    """Show current project status and data summary"""
    console.print("[bold blue]Project Status[/bold blue]")
    
    try:
        data_manager = DataManager()
        
        # Create status table
        table = Table(title="Data Summary")
        table.add_column("Data Type", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Last Updated", style="green")
        
        # Get counts
        member_count = len(data_manager.get_members())
        bill_count = len(data_manager.get_bills())
        
        table.add_row("Members", str(member_count), "N/A")
        table.add_row("Bills", str(bill_count), "N/A")
        
        console.print(table)
        
        # Check API key
        api_key = os.getenv('CONGRESS_API_KEY')
        if api_key:
            console.print("[green]✓ API key configured[/green]")
        else:
            console.print("[red]✗ API key not found in .env file[/red]")
            
    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")

if __name__ == '__main__':
    cli()
