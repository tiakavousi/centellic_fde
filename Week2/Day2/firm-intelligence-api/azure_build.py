"""
Create the Azure index and load every chunk into it
We run it from project root: python -m azure_buil
"""

import azure_store
import knowledge_store
import settings

def main() -> None:
    loaded = azure_store.build_index(knowledge_store.CHUNK_STARTEGY)
    print(f"Loaded {loaded} chunks into '{settings.AZURE_SEARCH_INDEX}' at {settings.AZURE_SEARCH_ENDPOINT}")


if __name__ == "__main__":
    main()