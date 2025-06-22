import json
import sys
from collections import Counter

def main():
    if len(sys.argv) != 2:
        print("Usage: python text_stats.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Load the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Calculate average document length
    total_words = 0
    all_emails = []
    docs_with_emails = 0

    for doc in data:
        body = doc.get('body', '')
        if body:
            # Tokenize and count words
            words = body.strip().split()
            total_words += len(words)
        
        # Extract emails from the 'emails' field
        emails = doc.get('emails', [])
        if emails:
            docs_with_emails += 1
            all_emails.extend(emails)
    
    avg_doc_length = total_words / len(data) if data else 0
    
    # Count email occurrences
    email_counts = Counter(all_emails)
    
    # Calculate percentage of documents with emails
    perc = docs_with_emails / len(data) if data else 0
    
    # Print results
    print(f"doc_len: {avg_doc_length:.3f}")
    print("emails:")
    for email, count in email_counts.most_common(10):
        print(f"\t('{email}', {count})")
    print(f"perc: {perc:.3f}")

if __name__ == "__main__":
    main()
