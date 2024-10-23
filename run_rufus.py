# run_rufus.py

import asyncio
import json
import logging
from datetime import datetime
from rufus import RufusClient
import os


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rufus_debug.log"),
        logging.StreamHandler()
    ]
)

async def main():
    # Retrieve API key from environment variables
    api_key = os.getenv('RUFUS_API_KEY')
    base_url = "https://simple.wikipedia.org/"  # Specify the URL here
    instructions = "Find information about wikipedia FAQ."  # Specify instructions here
    keywords = ["information", "FAQ"]  # Specify keywords here
    max_depth = 5
    max_pages = 200
    similarity_threshold = 0.3

    if not api_key:
        logging.error("No API Key provided. Exiting the crawler.")
        print("Error: No API Key provided. Please set the RUFUS_API_KEY environment variable.")
        return

    # Initialize RufusClient with parameters
    try:
        client = RufusClient(
            api_key=api_key,
            instructions=instructions,
            keywords=keywords,  # May be None
            max_depth=max_depth,
            max_pages=max_pages,
            similarity_threshold=similarity_threshold
        )
    except ValueError as ve:
        logging.error(f"Initialization Error: {ve}")
        print(f"Error: {ve}")
        return

    logging.info("Starting Rufus crawler.")

    # Run the crawler
    results = await client.scrape(base_url)

    logging.info("Crawling completed.")

    # Check if results are empty
    if not results:
        logging.warning("No relevant documents were extracted.")
        print("Warning: No relevant documents were extracted from this site.")
        print("Please try a different URL or adjust your instructions/keywords.")
    else:
        logging.info(f"Extracted {len(results)} relevant documents.")

        # Define the output filename with timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"rufus_output_{timestamp}.json"

        # Save the results to a JSON file
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info(f"Results successfully saved to {output_filename}")
            print(f"Results successfully saved to {output_filename}")
        except Exception as e:
            logging.error(f"Failed to save results to {output_filename}: {e}")
            print(f"Error: Failed to save results to {output_filename}.")

        # Optionally, print the results to the terminal
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

