# Building and Running the Rufus Application

In this section, I’ll walk you through the steps to build, set up, and run the Rufus application from scratch. This will involve installing dependencies, configuring the environment, and running the application both via the CLI and the API.

## Overview of Rufus

Rufus is a tool for extracting structured data from websites, focusing on relevance based on user-provided instructions and keywords. Rufus is designed to work efficiently in Retrieval-Augmented Generation (RAG) pipelines and provides both a command-line interface (CLI) and an API interface.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.7+**
- **Git**
- **Virtual Environment (optional but recommended)**
- **Playwright** (for dynamic content scraping)

## Step-by-Step Guide to Building the Rufus Application

### 1. Clone the Repository

First, clone the Rufus repository from GitHub.

```bash
git clone https://github.com/pranavsaji/rufus.git
cd rufus
```

### 2. Set Up a Virtual Environment

It’s best practice to create a virtual environment to manage dependencies.

- **Using `venv`:**

  ```bash
  python3 -m venv rufus_env
  source rufus_env/bin/activate  # On Windows: rufus_env\Scripts\activate
  ```

- **Using Conda:**

  ```bash
  conda create --name rufus_env python=3.9
  conda activate rufus_env
  ```

### 3. Install Dependencies

Rufus requires several Python libraries, which are listed in the `requirements.txt` file. Install them as follows:

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

Rufus uses Playwright to handle dynamic web content. To install the required Playwright browsers, run:

```bash
playwright install
```

### 5. Set Environment Variables

Rufus requires an API key for authentication when making API calls. Set this key in your environment as follows:

- **For Linux/macOS:**

  ```bash
  export RUFUS_API_KEY="aB3dE5fG7hJ9kL1mN2pQ4rS6tU8vW0xY"
  ```

- **For Windows (Command Prompt):**

  ```cmd
  set RUFUS_API_KEY="aB3dE5fG7hJ9kL1mN2pQ4rS6tU8vW0xY"
  ```

- **For Windows (PowerShell):**

  ```powershell
  $env:RUFUS_API_KEY="aB3dE5fG7hJ9kL1mN2pQ4rS6tU8vW0xY"
  ```

Alternatively, you can add this key to a `.env` file in the root directory:

```
# .env file
RUFUS_API_KEY=aB3dE5fG7hJ9kL1mN2pQ4rS6tU8vW0xY
```

### 6. Running Rufus via Command-Line (CLI)

You can run Rufus directly from the command-line using `run_rufus.py`.

#### Modify `run_rufus.py`

Open the `run_rufus.py` script and specify the target website URL and instructions:

```python
base_url = "https://www.example.com"
instructions = "Find information about product features and customer FAQs."
keywords = ["features", "FAQ", "pricing"]
max_depth = 3
max_pages = 100
similarity_threshold = 0.3
```

#### Run the CLI Application

Once the script is configured, run it as follows:

```bash
python run_rufus.py
```

**Expected Output:**

1. Rufus will crawl the website, extract relevant content, and save the results in a JSON file (e.g., `rufus_output_YYYYMMDD_HHMMSS.json`).
2. You’ll see a summary of the extracted content in the terminal output.

### 7. Running Rufus via API

Rufus can also be used via its API, allowing programmatic access.

#### Start the API Server

Start the API server by running the `api_server.py` script:

```bash
python api_server.py
```

This will start the FastAPI server on `http://localhost:8000`.

You can check the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

#### Example API Call

You can now interact with Rufus via the API using the `api_client.py` script or by making HTTP requests from your own client. Below is an example of an API call using Python’s `requests` library:

```python
import requests
import os

API_URL = "http://localhost:8000/scrape"
API_KEY = os.getenv('RUFUS_API_KEY')

payload = {
    "base_url": "https://www.example.com",
    "instructions": "Find information about product features and customer FAQs.",
    "keywords": ["features", "FAQ", "pricing"],
    "max_depth": 3,
    "max_pages": 100,
    "similarity_threshold": 0.3
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

response = requests.post(API_URL, json=payload, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
```

#### API Response

The API will return a JSON object containing the extracted content, similar to the following:

```json
[
    {
        "url": "https://www.example.com/features",
        "content": "Our product offers a range of features including..."
    },
    {
        "url": "https://www.example.com/faq",
        "content": "Frequently asked questions about our product..."
    }
]
```

## Approach

### Problem Addressed

Rufus was designed to address the challenges of extracting relevant information from dynamic, multi-layered websites. Traditional web scraping tools often extract the entire webpage without considering the relevance of the content. Rufus improves this by intelligently navigating and filtering the content based on user-provided instructions.

### Challenges Faced and Overcoming Them

1. **Handling Dynamic Web Content:** Many websites load content via JavaScript, which was a major scraping challenge. To solve this, Rufus uses Playwright to render dynamic content and interact with JavaScript-heavy websites.

2. **Ensuring Content Relevance:** Not all extracted content is useful. To filter irrelevant data, I implemented a similarity computation mechanism using `sentence-transformers`. This ensures that only the most relevant information is extracted based on user-defined instructions and keywords.

3. **Managing Large Websites:** Some websites have hundreds of pages. To prevent overloading, Rufus uses parameters such as `max_depth` and `max_pages` to limit the number of pages crawled.

4. **Scalability:** Rufus is designed to be flexible, allowing users to control the depth of crawling, number of pages, and relevance threshold. This ensures it works efficiently on both small and large websites.

### How Rufus Works

1. **User Instructions:** Rufus takes user instructions and keywords that define the type of content to search for (e.g., "Find FAQs and product features").
2. **Crawling:** Rufus navigates the website, respecting the `max_depth` and `max_pages` parameters, and extracts all content.
3. **Relevance Filtering:** Using Natural Language Processing (NLP), Rufus calculates the similarity between the extracted content and the user instructions. Only relevant content is retained.
4. **Output:** The relevant content is saved in JSON format, ready for use in Retrieval-Augmented Generation (RAG) systems.

## Integrating Rufus into a RAG Pipeline

Rufus can be seamlessly integrated into RAG pipelines for real-time information retrieval. Here’s how:

1. **Run Rufus:** Use either the CLI or API to extract structured data from websites based on the user’s specific needs.
2. **Store Extracted Data:** Store the output in a database or vector store for future retrieval. This output can be used as a knowledge base for your RAG pipeline.
3. **Query the Knowledge Base:** When a user asks a question, the RAG model can retrieve relevant information from the knowledge base created by Rufus.
4. **Feed into LLM:** The retrieved documents can then be fed into a large language model (LLM) to generate an accurate and contextually relevant response.

### Example Integration Flow:

- **Step 1:** Rufus scrapes the website and stores relevant content in a database (e.g., FAQ pages).
- **Step 2:** A user submits a question (e.g., "What features does the product offer?").
- **Step 3:** The RAG system queries the database for relevant content.
- **Step 4:** The retrieved content is fed into a language model (e.g., GPT) to generate the final answer.


## Conclusion

Rufus is an efficient, scalable tool for extracting relevant web content that integrates seamlessly into Retrieval-Augmented Generation pipelines. With Rufus, you can automate the process of gathering website data, filtering it based on instructions, and preparing it for use in modern AI-powered systems.

By providing both a CLI and API interface, Rufus ensures flexibility, making it an ideal choice for developers looking to integrate web scraping into their applications.

## Note

**Important:** Since the task was to take content for the purpose of this case study, i bypassed a website's `robots.txt` file. But as an ethical practice its always best to respect a website's `robots.txt` file and terms of service when scraping data.