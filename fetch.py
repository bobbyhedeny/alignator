#!/usr/bin/env python3
"""
Simple example script for fetching data from Congress.gov API
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.congress_client import CongressClient
from src.data.data_manager import DataManager

def main():
    """Main function to demonstrate API usage"""
    # Load environment variables
    load_dotenv()
    
    print("🏛️ Alignator - Congress.gov API Example")
    print("=" * 50)
    
    try:
        # Initialize components
        client = CongressClient()
        data_manager = DataManager()
        
        print("✓ API client initialized")
        
        # Fetch some basic data
        print("\n📊 Fetching Congress members...")
        members = client.get_members(congress=118, chamber="both")
        print(f"✓ Found {len(members)} members")
        
        # Save to database
        data_manager.save_members(members)
        print("✓ Members saved to database")
        
        # Show some sample data
        if members:
            print("\n👥 Sample Members:")
            for i, member in enumerate(members[:5]):
                print(f"  {i+1}. {member.get('name', 'N/A')} ({member.get('party', 'N/A')}) - {member.get('state', 'N/A')}")
        
        # Fetch some bills
        print("\n📜 Fetching bills...")
        bills = client.get_bills(congress=118, limit=10)
        print(f"✓ Found {len(bills)} bills")
        
        # Save to database
        data_manager.save_bills(bills)
        print("✓ Bills saved to database")
        
        # Show some sample bills
        if bills:
            print("\n📋 Sample Bills:")
            for i, bill in enumerate(bills[:3]):
                title = bill.get('title', 'N/A')
                if len(title) > 80:
                    title = title[:77] + "..."
                print(f"  {i+1}. {title}")
        
        print("\n✅ Data fetching complete!")
        print("\nNext steps:")
        print("1. Run 'python main.py status' to check your data")
        print("2. Run 'python main.py analyze-alignment' to analyze political alignment")
        print("3. Run 'python main.py dashboard' to launch the interactive dashboard")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set up your CONGRESS_API_KEY in a .env file")
        print("2. Installed all dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
