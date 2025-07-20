import os
import pickle
import math
from collections import defaultdict, Counter
from tqdm import tqdm
from nltk import pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from datasets import load_dataset
from rank_bm25 import BM25Okapi

class Indexer:
    dbfile = "./ir.idx"  # You need to store index file on your disk so that you don't need to
                         # re-index when running the program again. You can name this file however
                         # you like. (e.g., index.pkl)

    def __init__(self):
        # TODO. You will need to create appropriate data structures for the following elements
        self.tok2idx = {}                       # map (token to id)
        self.idx2tok = {}                       # map (id to token)
        self.postings_lists = defaultdict(dict) # postings for each word: term_id -> {doc_id: freq}
        self.docs = []                          # list of tokenized docs
        self.raw_ds = None                      # raw documents for result presentation
        self.corpus_stats = {'avgdl': 0}        # any corpus-level statistics
        self.stopwords = set(stopwords.words('english'))
        self.tokenizer = RegexpTokenizer(r"\w+")
        self.lemmatizer = WordNetLemmatizer()

        if os.path.exists(self.dbfile):
            # TODO. If these exists a saved corpus index file, load it.
            # (You may use pickle to save and load a python object.)
            with open(self.dbfile, 'rb') as f:
                obj = pickle.load(f)
            self.tok2idx = obj['tok2idx']
            self.idx2tok = obj['idx2tok']
            self.postings_lists = obj['postings_lists']
            self.docs = obj['docs']
            self.raw_ds = obj['raw_ds']
            self.corpus_stats = obj['corpus_stats']
            print(f"Loaded index from {self.dbfile}")
        else:
            # TODO. Load CNN/DailyMail dataset, preprocess and create postings lists.
            ds = load_dataset("cnn_dailymail", '3.0.0', split="test")
            self.raw_ds = ds['article']
            self.clean_text(self.raw_ds)
            self.create_postings_lists()
            with open(self.dbfile, 'wb') as f:
                pickle.dump({
                    'tok2idx': self.tok2idx,
                    'idx2tok': self.idx2tok,
                    'postings_lists': self.postings_lists,
                    'docs': self.docs,
                    'raw_ds': self.raw_ds,
                    'corpus_stats': self.corpus_stats
                }, f)
            print(f"Index saved to {self.dbfile}")

    def clean_text(self, lst_text, query=False):
        # TODO. this function will run in two modes: indexing and query mode.
        # TODO. run simple whitespace-based tokenizer (e.g., RegexpTokenizer)
        # TODO. run lemmatizer (e.g., WordNetLemmatizer)
        # TODO. read documents one by one and process
        cleaned = []
        for text in lst_text:
            tokens = []
            for tok in self.tokenizer.tokenize(text.lower()):
                if tok in self.stopwords:
                    continue
                lemma = self.lemmatizer.lemmatize(tok)
                tokens.append(lemma)
            cleaned.append(tokens)
        if query:
            return cleaned[0] if cleaned else []
        self.docs = cleaned
        total_len = sum(len(d) for d in self.docs)
        self.corpus_stats['avgdl'] = total_len / len(self.docs)

    def create_postings_lists(self):
        # TODO. This creates postings lists of your corpus
        # TODO. While indexing compute avgdl and document frequencies of your vocabulary
        # TODO. Save it, so you don't need to do this again in the next runs.
        # Save
        for doc_id, tokens in enumerate(tqdm(self.docs, desc='Building postings')):
            freqs = Counter(tokens)
            for tok, freq in freqs.items():
                if tok not in self.tok2idx:
                    term_id = len(self.tok2idx)
                    self.tok2idx[tok] = term_id
                    self.idx2tok[term_id] = tok
                else:
                    term_id = self.tok2idx[tok]
                self.postings_lists[term_id][doc_id] = freq

class SearchAgent:
    k1 = 1.5                # BM25 parameter k1 for tf saturation
    b = 0.75                # BM25 parameter b for document length normalization

    def __init__(self, indexer):
        # TODO. set necessary parameters
        self.i = indexer
        self.N = len(self.i.docs)
        self.avgdl = self.i.corpus_stats['avgdl']

    def query(self, q_str):

        # 1) clean & tokenize
        q_tokens = self.i.clean_text([q_str], query=True)
        if not q_tokens:
            print("No query terms matched the index.")
            return None

        # 2) BM25 ranking using rank_bm25
        bm25 = BM25Okapi(self.i.docs, k1=self.k1, b=self.b)
        scores = bm25.get_scores(q_tokens)
        if not any(scores):
            print("No results found.")
            return None

        # 3) sort and display
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        self.display_results(ranked[:5])
        return None

    def display_results(self, hits, snippet_len=200, score_fmt=".12f"):
        # Decode
        # TODO, the following is an example code, you can change however you would like.
        for docid, score in hits[:5]:  # print top 5 results
            print()
            print(f"DocID: {docid}")
            print(f"Score: {score:{score_fmt}}")
            print("Article:")
            text = self.i.raw_ds[docid].replace("\n", " ").strip()
            snippet = text[:snippet_len] + ("..." if len(text) > snippet_len else "")
            print(snippet)

if __name__ == "__main__":
    i = Indexer()
    q = SearchAgent(i)
    import code
    code.interact(local=dict(globals(), **locals()))