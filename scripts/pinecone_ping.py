import os
import sys
from pinecone import Pinecone

def test_pinecone_connectivity():
    """
    Checks the connectivity and status of the 'homelab' Pinecone index.
    Expects PINECONE_API_KEY environment variable to be set.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Error: PINECONE_API_KEY environment variable not set.")
        print("Please set it from your Vaultwarden (FraWo organization) vault.")
        sys.exit(1)

    try:
        pc = Pinecone(api_key=api_key)
        
        index_name = "homelab"
        
        # Check if index exists
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        
        if index_name not in index_names:
            print(f"Error: Index '{index_name}' not found in your Pinecone account.")
            print(f"Available indexes: {', '.join(index_names)}")
            sys.exit(1)
            
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        
        print(f"✅ Successfully connected to Pinecone!")
        print(f"Index: {index_name}")
        print(f"Stats: {stats}")
        
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_pinecone_connectivity()
