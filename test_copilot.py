import pandas as pd
from pap_ai_era.copilot import CopilotPapaiera

def main():
    print("Initializing PapAiEra Copilot...")
    copilot = CopilotPapaiera()
    
    query = "Why is the paper surface draggy or picking on the press rolls?"
    print(f"\nUser Question: {query}")
    
    print("\n[Local Search Results]")
    results = copilot.search_knowledge(query, top_n=2)
    for r in results:
        print(f"--- Page {r['metadata']['page']} --- (Score: {r['score']:.2f})")
        print(r['text'])
        print()
        
    print("\nSuccess! The local knowledge base is working properly.")
    
if __name__ == "__main__":
    main()
