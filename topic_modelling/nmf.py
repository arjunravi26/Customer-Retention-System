import re
import nltk
from nltk.corpus import stopwords
import spacy
from gensim.models import Phrases
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any
from data import fetch_data
from logger import logging


def download_resources():
    """
    Download NLTK stopwords and ensure spaCy model is available.
    """
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')


class TextPreprocessor:
    def __init__(self, lemmatizer_model: str = 'en_core_web_sm'):
        download_resources()
        self.stop_words = set(stopwords.words('english'))
        self.nlp = spacy.load(lemmatizer_model, disable=['parser', 'ner'])

    def clean_and_tokenize(self, documents):
        cleaned = [re.sub(r"[^a-zA-Z0-9 ]+", " ", re.sub(r"\s+", " ", doc)).lower()
                   for doc in documents]
        return [[t for t in doc.split() if t not in self.stop_words and len(t) > 2]
                for doc in cleaned]

    def build_ngrams(self, tokenized, min_count=5, threshold=100):
        bigram = Phrases(tokenized, min_count=min_count, threshold=threshold)
        trigram = Phrases(bigram[tokenized], min_count=min_count, threshold=threshold)
        return [trigram[bigram[doc]] for doc in tokenized]

    def lemmatize(self, ngrams):
        lemmatized = []
        for doc in ngrams:
            spacy_doc = self.nlp(" ".join(doc))
            tokens = [token.lemma_ for token in spacy_doc
                      if token.lemma_ not in self.stop_words and len(token.lemma_) > 2]
            lemmatized.append(tokens)
        return lemmatized

    def preprocess(self, documents):
        tokens = self.clean_and_tokenize(documents)
        ngrams = self.build_ngrams(tokens)
        lemmatized = self.lemmatize(ngrams)
        joined = [" ".join(doc) for doc in lemmatized]
        return lemmatized, joined


class TopicModelingPipeline:
    def __init__(self, n_topics=5):
        self.n_topics = n_topics
        self.nmf_model = None
        self.vectorizer = None

    def fit_nmf(self, documents):
        try:
            # TF-IDF Vectorization
            self.vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
            doc_term_matrix = self.vectorizer.fit_transform(documents)

            # NMF Model Fitting
            self.nmf_model = NMF(n_components=self.n_topics, random_state=42)
            self.nmf_model.fit(doc_term_matrix)
            return self.nmf_model
        except Exception as e:
            logging.exception(f"Failed to fit NMF model: {str(e)}")
            raise ValueError(f"Failed to fit NMF model: {str(e)}")

    def get_nmf_results(self) -> Dict[str, Any]:
        try:
            # Extract topics and their top words
            terms = self.vectorizer.get_feature_names_out()
            topics = []
            for topic_idx, topic in enumerate(self.nmf_model.components_):
                top_idx = topic.argsort()[-10:][::-1]  # Get top 10 words per topic
                top_words = [terms[i] for i in top_idx]
                topic_name = " ".join(top_words[:2]).title()
                description = f"Topics related to {', '.join(top_words[:5])}"

                topics.append({
                    "topic_id": topic_idx,
                    "topic_name": topic_name,
                    "description": description,
                    "top_words": top_words
                })

            return {"topics": topics}
        except Exception as e:
            logging.exception(f"Exception in topic model pipeline {str(e)}")
            raise ValueError(f"Failed to generate NMF results: {str(e)}")


if __name__ == '__main__':
    docs = fetch_data()
    preprocessor = TextPreprocessor()
    tokens, cleaned = preprocessor.preprocess(docs)

    pipeline = TopicModelingPipeline(n_topics=6)
    try:
        nmf_model = pipeline.fit_nmf(cleaned)
        results = pipeline.get_nmf_results()
        print("Results:", results)
    except Exception as e:
        print(f"Error: {str(e)}")
