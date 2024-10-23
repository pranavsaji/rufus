# api_client.py

import requests
import os
import json

def main():
    # Define the API endpoint
    API_URL = "http://localhost:8000/scrape"

    # Your API Key
    API_KEY = os.getenv('RUFUS_API_KEY')  # Ensure this is set in your environment

    if not API_KEY:
        print("Error: RUFUS_API_KEY environment variable not set.")
        return

    # Define the payload
    payload = {
        "base_url": "https://simple.wikipedia.org/",
        "instructions": "Find information about wikipedia.",
        "keywords": ["features", "FAQ", "pricing"],
        "max_depth": 5,
        "max_pages": 200,
        "similarity_threshold": 0.3
    }

    # Define the headers with the API Key
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Make the POST request
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

    # Handle the response
    if response.status_code == 200:
        try:
            documents = response.json()
            print("Scraped Documents:")
            for doc in documents:
                print(f"URL: {doc['url']}\nContent: {doc['content'][:200]}...\n")
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
    elif response.status_code == 401:
        print("Authentication Failed: Invalid API Key.")
    elif response.status_code == 404:
        print("No relevant documents were extracted.")
    else:
        try:
            error_detail = response.json().get('detail', 'No detail provided.')
        except json.JSONDecodeError:
            error_detail = "No detail provided."
        print(f"Error {response.status_code}: {error_detail}")

if __name__ == "__main__":
    main()
