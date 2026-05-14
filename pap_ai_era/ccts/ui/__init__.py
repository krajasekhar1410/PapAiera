"""
Runs the PapAiEra CCTS UI.
Usage: python -m pap_ai_era.ccts.ui.app
"""
import subprocess
import sys
import os

def main():
    app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path,
                    '--server.headless=true'], check=True)

if __name__ == '__main__':
    main()
