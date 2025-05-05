import re
import nltk
from nltk.corpus import stopwords
import spacy
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from top2vec import Top2Vec
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
        bigram = Phraser(Phrases(tokenized, min_count=min_count, threshold=threshold))
        trigram = Phraser(Phrases(bigram[tokenized], min_count=min_count, threshold=threshold))
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

    def fit_top2vec(self, documents, embedding_model='all-MiniLM-L6-v2'):
        try:
            model = Top2Vec(documents,
                            embedding_model=embedding_model,
                            speed='deep-learn',
                            workers=4,
                            min_count=5)
            model.hierarchical_topic_reduction(self.n_topics)
            return model
        except Exception as e:
            logging.exception(f"Failed to fit Top2Vec model: {str(e)}")
            raise ValueError(f"Failed to fit Top2Vec model: {str(e)}")

    def get_top2vec_results(self, model, documents) -> Dict[str,Any]:
        """
        Generate Top2Vec results in a format matching generate_mock_topics.

        Args:
            model: Trained Top2Vec model
            documents: List of preprocessed documents

        Returns:
            Dictionary with topics and document assignments
        """
        try:
            sizes, topic_nums = model.get_topic_sizes()
            topic_words, word_scores, _ = model.get_topics(len(topic_nums))

            results = {
                "topics": [],
            }

            # Create a dictionary of topic sizes for lookup
            topic_size_dict = dict(zip(topic_nums, sizes))
            logging.info("Topic sizes:", topic_size_dict)

            # Add topics with name, description, frequency, and mentions
            for topic_id, words, size in zip(topic_nums, topic_words, sizes):
                topic_name = " ".join(words[:2]).title()
                description = f"Topics related to {', '.join(words[:5])}"
                topic_data = {
                    "topic_id": int(topic_id),
                    "topic_name": topic_name,
                    "description": description,
                    "frequency": int(size),
                }
                results["topics"].append(topic_data)

            return results
        except Exception as e:
            logging.exception(f"Exception in topic model pipeline {str(e)}")
            raise ValueError(f"Failed to generate Top2Vec results: {str(e)}")


if __name__ == '__main__':
    docs = fetch_data()
    preprocessor = TextPreprocessor()
    tokens, cleaned = preprocessor.preprocess(docs)

    pipeline = TopicModelingPipeline(n_topics=6)
    try:
        t2v = pipeline.fit_top2vec(cleaned)
        results = pipeline.get_top2vec_results(t2v, cleaned)
        print("Results:", results)
    except Exception as e:
        print(f"Error: {str(e)}")