import json
import re
import string
from collections import Counter
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from tabulate import tabulate

# Download NLTK stopwords if not already downloaded
nltk.download('stopwords')

# Get the list of English stopwords from NLTK
STOPWORDS = set(stopwords.words('english'))

def tokenize(text, remove_numbers=False, remove_stopwords=False, remove_punctuation=False):
    """
    Tokenize text into words with options to remove numbers, stopwords, and punctuation.
    """
    # Extract words using regex
    tokens = re.findall(r'\b\w+\b', text.lower())
    
    # Remove numbers if specified
    if remove_numbers:
        tokens = [token for token in tokens if not token.isdigit()]
    
    # Remove stopwords if specified
    if remove_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]
    
    # Remove punctuation if specified
    if remove_punctuation:
        tokens = [token for token in tokens if token not in string.punctuation]
    
    return tokens

def format_table(word_counts, total_words):
    """Format the word frequency data into the desired table format."""
    rows = []
    for rank, (word, freq) in enumerate(word_counts.most_common(30), start=1):
        perc = freq / total_words
        rows.append([rank, word, freq, f"{perc:.3f}"])
    return rows

def plot_zipf_distribution(word_counts, top_n=1000):
    """Plot Zipf-like word frequency distribution (rank vs. frequency)."""
    frequencies = sorted(word_counts.values(), reverse=True)[:top_n]

    plt.figure(figsize=(8, 6))
    plt.plot(range(1, len(frequencies) + 1), frequencies, linewidth=1)
    plt.xlabel("rank")
    plt.ylabel("frequency")
    plt.title("Word Frequency Distribution (Zipf's Law)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def plot_zipf_loglog(word_counts, top_n=1000):
    """Plot word frequency distribution on log-log scale."""
    frequencies = sorted(word_counts.values(), reverse=True)[:top_n]
    ranks = range(1, len(frequencies) + 1)

    plt.figure(figsize=(8, 6))
    plt.plot(ranks, frequencies)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('rank')
    plt.ylabel('log occurrences')
    plt.title("Word Frequency Distribution (Log-Log Scale)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def main():
    # Load the JSON file
    json_file = "ksu1000.json"  # Replace with your JSON file path
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Collect all words from the 'body' field
    all_words = []
    for doc in data:
        body = doc.get('body', '')
        if body:
            words = tokenize(body)
            all_words.extend(words)
    
    # First Pass: Remove numbers but include stopwords
    words_first_pass = tokenize(" ".join(all_words), remove_numbers=True, remove_stopwords=False)
    word_counts_first_pass = Counter(words_first_pass)
    total_words_first_pass = sum(word_counts_first_pass.values())
    top_30_first_pass = format_table(word_counts_first_pass, total_words_first_pass)
    
    # Second Pass: Remove stopwords, numbers, and punctuation
    words_second_pass = tokenize(" ".join(all_words), remove_numbers=True, remove_stopwords=True, remove_punctuation=True)
    word_counts_second_pass = Counter(words_second_pass)
    total_words_second_pass = sum(word_counts_second_pass.values())
    top_30_second_pass = format_table(word_counts_second_pass, total_words_second_pass)
    
    # Print results
    print("\nTop 30 most common words before removing stopwords\n")
    print(tabulate(top_30_first_pass, headers=["Rank", "Term", "Freq.", "Perc."], tablefmt="plain"))
    
    print("\nTop 30 most common words after removing stopwords and punctuation\n")
    print(tabulate(top_30_second_pass, headers=["Rank", "Term", "Freq.", "Perc."], tablefmt="plain"))
    
    # Plot Viewer
    while True:
        print("\n------------------------------------------------------\n")
        print("Please choose which plot to view:\n")
        print("1. Word Distribution (Before Removing Stopwords and Punctuation)\n")
        print("2. Zipf-like Distribution (Log-Log)\n")
        print("3. Exit Viewer\n")
        print("------------------------------------------------------\n")

        try:
            choice = int(input("Enter your choice (1/2/3): "))
            if choice == 1:
                plot_zipf_distribution(word_counts_first_pass)
                plt.close()
            elif choice == 2:
                plot_zipf_loglog(word_counts_first_pass)
                plt.close()
            elif choice == 3:
                print("Exiting viewer.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid integer.")


if __name__ == "__main__":
    main()