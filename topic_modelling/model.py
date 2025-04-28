import data
from sklearn.decomposition import NMF
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import spacy
import gensim
from gensim.models import Phrases
from gensim.corpora import Dictionary
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from bertopic import BERTopic
from top2vec import Top2Vec


customer_data = data.fetch_data()
# print(customer_data)
# print(customer_data[0])

# === Setup ===
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
# print(stop_words)

# === Preprocessing ===
def preprocess(texts):
    """
    Clean, tokenize, lemmatize, and build bigrams/trigrams.
    Returns list of lemmatized tokens and joined strings.
    """
    # Basic cleanup
    cleaned = []
    for doc in texts:
        doc = re.sub(r"\s+", " ", doc)
        doc = re.sub(r"[^a-zA-Z0-9 ]", " ", doc)
        cleaned.append(doc.lower())
    # print(cleaned)
    # Tokenize and remove stopwords
    tokenized = []
    for doc in cleaned:
        tokens = [token for token in re.split(r"\s+", doc) if token and token not in stop_words]
        tokenized.append(tokens)
    # print(tokenized)

    # Build bigrams and trigrams
    bigram = Phrases(tokenized, min_count=5, threshold=100)
    trigram = Phrases(bigram[tokenized], min_count=5, threshold=100)
    tokens_ngrams = [trigram[bigram[doc]] for doc in tokenized]
    # print(bigram)
    # print(trigram)
    # print(tokens_ngrams)

    # Lemmatize
    lemmatized = []
    for doc in tokens_ngrams:
        spacy_doc = nlp(" ".join(doc))
        lemmatized.append([token.lemma_ for token in spacy_doc if token.lemma_ not in stop_words and len(token.lemma_) > 2])

    joined = [" ".join(doc) for doc in lemmatized]
    return lemmatized, joined

lemmatized,cleaned_data = preprocess(customer_data)

print(lemmatized[:5])
print(cleaned_data[:5])


dictionary = corpora.Dictionary(lemmatized)

# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
doc_term_matrix = [dictionary.doc2bow(doc) for doc in lemmatized]


print(doc_term_matrix[:5])
# Creating the object for LDA model using gensim library
Lda = gensim.models.ldamodel.LdaModel

# Running and Trainign LDA model on the document term matrix.
ldamodel = Lda(doc_term_matrix, num_topics=5, id2word = dictionary, passes=50)
print(ldamodel.print_topics(num_topics=5, num_words=3))


vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(cleaned_data)

# Apply LSA (Truncated SVD)
lsa_model = TruncatedSVD(n_components=3, random_state=1)
lsa_topic_matrix = lsa_model.fit_transform(X)

# Print the topics
terms = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lsa_model.components_):
    print(f"Topic #{topic_idx}:")
    print(" ".join([terms[i] for i in topic.argsort()[:-6:-1]]))

nmf_model = NMF(n_components=3, random_state=1)
W = nmf_model.fit_transform(X)
H = nmf_model.components_

# Print the topics
terms = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(H):
    print(f"Topic #{topic_idx}:")
    print(" ".join([terms[i] for i in topic.argsort()[:-6:-1]]))

# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('all-MiniLM-L6-v2')

model = Top2Vec(cleaned_data, embedding_model="all-MiniLM-L6-v2",contextual_top2vec=True, speed="learn", workers=4,min_count=5)

# Retrieve the number of topics
print(f"Number of topics: {model.get_num_topics()}")

# Display the top words for each topic
# for topic_num in range(model.get_num_topics()):
#     words = model.get_topics(topic_num)
#     print(f"Topic {topic_num}: {words[:5]}")

print(model.get_topic_sizes())
topic_words, word_scores, topic_nums = model.get_topics(10)
print(f"Topic 77: {topic_words, word_scores, topic_nums }")

print(model.get_document_topic_distribution())
print(model.get_document_topic_relevance())
print(model.get_document_token_topic_assignment())
print(model.get_document_tokens())

topic_words, word_scores, topic_scores, topic_nums = model.search_topics(keywords=["medicine"], num_topics=5)
print(topic_words, word_scores, topic_scores, topic_nums)
for topic in topic_nums:
    model.generate_topic_wordcloud(topic)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(cleaned_data)

# Get current topic info
topic_info = topic_model.get_topic_info()
print(topic_info)
