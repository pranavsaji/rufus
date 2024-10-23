# rufus/utils.py

from typing import List, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# Ensure required NLTK data packages are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize the model once
logger.debug("Loading SentenceTransformer model.")
model = SentenceTransformer('all-MiniLM-L6-v2')
logger.debug("Model loaded successfully.")

def extract_keywords(instructions: str, num_keywords: int = 5) -> List[str]:
    """
    Extracts keywords from the user instructions using NLP techniques.
    
    :param instructions: User-defined instructions for relevance.
    :param num_keywords: Number of top keywords to extract.
    :return: A list of extracted keywords.
    """
    try:
        # Tokenize the instructions
        tokens = word_tokenize(instructions.lower())
        logger.debug(f"Tokenized instructions: {tokens}")
        
        # Remove stopwords and non-alphabetic tokens
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
        logger.debug(f"Filtered tokens: {filtered_tokens}")
        
        # Count word frequencies
        word_counts = Counter(filtered_tokens)
        logger.debug(f"Word counts: {word_counts}")
        
        # Extract the most common words as keywords
        most_common = word_counts.most_common(num_keywords)
        keywords = [word for word, count in most_common]
        logger.debug(f"Extracted keywords: {keywords}")
        
        return keywords
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []

def compute_similarity(content: str, instructions: str, keywords: Optional[List[str]] = None, threshold: float = 0.5) -> bool:
    """
    Compute the similarity between the content and instructions.
    Returns True if similarity is above the threshold and contains relevant keywords.

    :param content: Extracted text content from a webpage.
    :param instructions: User-defined instructions for relevance.
    :param keywords: List of relevant keywords.
    :param threshold: Similarity threshold for relevance.
    :return: Boolean indicating if content is relevant.
    """
    try:
        embeddings = model.encode([instructions, content])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        logger.debug(f"Computed similarity: {similarity}")
        
        if keywords:
            content_lower = content.lower()
            has_keywords = any(keyword.lower() in content_lower for keyword in keywords)
            logger.debug(f"Contains relevant keywords: {has_keywords}")
        else:
            # If no keywords are provided, consider it as True (since keywords are optional)
            has_keywords = True
            logger.debug("No keywords provided; bypassing keyword check.")
        
        return similarity > threshold and has_keywords
    except Exception as e:
        logger.error(f"Error computing similarity: {e}")
        return False
