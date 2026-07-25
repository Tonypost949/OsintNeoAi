#!/usr/bin/env python3
"""
OSINT Complete Setup & Runner
=============================
Single-command setup and execution of entire OSINT suite.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n{'='*80}")
    print(f"📦 {description}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("🔍 OSINT INTELLIGENCE SUITE - COMPLETE SETUP")
    print("="*80)
    
    # Step 1: Install dependencies
    print("\n📋 Checking Python version...")
    python_version = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
    print(f"   {python_version.stdout.strip()}")
    
    # Step 2: Install requirements
    run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )
    
    # Step 3: Run aggregator
    print("\n" + "="*80)
    print("🌐 Repository Aggregation (Optional)")
    print("="*80)
    
    if input("\nRun repository aggregator? (y/n): ").lower() == 'y':
        github_user = input("GitHub username [Tonypost949]: ") or "Tonypost949"
        run_command(
            f"{sys.executable} osint_repo_aggregator.py {github_user}",
            f"Aggregating OSINT repos for {github_user}"
        )
    
    # Step 4: Run main suite
    print("\n" + "="*80)
    print("🎯 OSINT Workbook Suite")
    print("="*80)
    
    use_sample = input("\nUse sample data? (y/n): ").lower() != 'n'
    
    if use_sample:
        run_command(
            f"{sys.executable} osint_main.py --all",
            "Running complete OSINT workflow"
        )
    else:
        input_file = input("Input file path: ")
        output_file = input("Output file path [osint_results.xlsx]: ") or "osint_results.xlsx"
        
        run_command(
            f"{sys.executable} osint_main.py --input {input_file} --output {output_file} --all",
            "Running complete OSINT workflow"
        )
    
    # Step 5: Start dashboard
    print("\n" + "="*80)
    print("🚀 Starting Interactive Dashboard")
    print("="*80)
    
    if input("\nStart Streamlit dashboard? (y/n): ").lower() == 'y':
        print("\n🌐 Opening dashboard at http://localhost:8501")
        subprocess.run(f"{sys.executable} -m streamlit run osint_dashboard.py", shell=True)
    
    print("\n" + "="*80)
    print("✅ OSINT Setup Complete!")
    print("="*80)
    print("""
    Next steps:
    1. Review generated Excel workbook
    2. Check HTML network visualization
    3. Explore JSON report for detailed data
    4. Run dashboard: python3 osint_dashboard.py
    """)

if __name__ == '__main__':
    main()
