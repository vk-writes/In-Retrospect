import os
import re
import spacy
import json
from collections import Counter, defaultdict
from datetime import datetime
from textstat import flesch_reading_ease, flesch_kincaid_grade
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import yake  # Lightweight keyword extractor (no NLTK!)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Configuration
EXCLUDED_FILES = {
    'index.html', 'stats.html', 'about.html', 'contact.html',
    'style.css', 'style2.css', 'navbar.js', '404.html'
}
STOPWORDS = {
    'the', 'and', 'of', 'to', 'a', 'in', 'that', 'it', 'is', 'was',
    'for', 'with', 'on', 'as', 'at', 'by', 'this', 'be', 'are'
}

POS_FULL_NAMES = {
    "ADJ": "Adjectives",
    "ADP": "Adpositions (Prepositions and Postpositions)",
    "ADV": "Adverbs",
    "AUX": "Auxiliary Verbs",
    "CONJ": "Coordinating Conjunctions",
    "CCONJ": "Coordinating Conjunctions",
    "DET": "Determiners",
    "INTJ": "Interjections",
    "NOUN": "Nouns",
    "NUM": "Numerals",
    "PART": "Particles",
    "PRON": "Pronouns",
    "PROPN": "Proper Nouns",
    "PUNCT": "Punctuation",
    "SCONJ": "Subordinating Conjunctions",
    "SYM": "Symbols",
    "VERB": "Verbs",
    "X": "Other",
    "SPACE": "Spaces",
}

def analyze_articles():
    total_words = 0
    articles = []
    word_counter = Counter()
    pos_counters = defaultdict(Counter)
    lexical_diversities = {}
    sentence_stats = {}
    readabilities = {}
    sentiments = {}
    entity_counter = Counter()
    keywords = {}
    all_text_for_wordcloud = []

    # YAKE configuration
    kw_extractor = yake.KeywordExtractor(
        lan="en", n=3, dedupLim=0.9, top=10, stopwords=STOPWORDS
    )

    print("Scanning articles...")
    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            print(f"  Processing {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                raw_html = f.read()
                text = re.sub(r'<[^>]+>', ' ', raw_html)
                doc = nlp(text.lower())

                articles.append(filename)
                total_words += len(doc)

                # Word counts and POS
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        word_counter[token.text] += 1
                        pos_counters[token.pos_][token.text] += 1

                # Lexical diversity
                words = [t.text for t in doc if t.is_alpha]
                lexical_diversities[filename] = len(set(words)) / len(words) if words else 0

                # Sentence stats
                doc_full = nlp(text)
                lengths = [len(sent) for sent in doc_full.sents]
                avg_sentence_length = sum(lengths) / len(lengths) if lengths else 0
                longest_sentence_length = max(lengths) if lengths else 0
                sentence_stats[filename] = {
                    'avg_sentence_length': avg_sentence_length,
                    'longest_sentence_length': longest_sentence_length,
                    'sentence_count': len(lengths)
                }

                # Readability
                flesch_score = flesch_reading_ease(text)
                fk_grade = flesch_kincaid_grade(text)
                readabilities[filename] = {
                    'flesch_reading_ease': flesch_score,
                    'flesch_kincaid_grade': fk_grade
                }

                # Sentiment
                blob = TextBlob(text)
                sentiments[filename] = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }

                # NER
                doc_ner = nlp(text)
                for ent in doc_ner.ents:
                    entity_counter[ent.label_] += 1

                # Keyword extraction with YAKE
                extracted_keywords = kw_extractor.extract_keywords(text)
                keywords[filename] = [kw for kw, _ in extracted_keywords]

                all_text_for_wordcloud.append(text)

    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"

    # Generate word cloud image
    combined_text = " ".join(all_text_for_wordcloud)
    wc = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(combined_text)
    wc.to_file("wordcloud.png")

    stats = {
        'article_count': len(articles),
        'total_words': total_words,
        'avg_words': total_words // len(articles) if articles else 0,
        'top_words': [w for w, _ in word_counter.most_common(10)],
        'longest_article': longest_article.replace('.html', ''),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
        'pos_summary': {
            pos: [w for w, _ in words.most_common(5)]
            for pos, words in sorted(pos_counters.items())
        },
        'lexical_diversities': lexical_diversities,
        'sentence_stats': sentence_stats,
        'readabilities': readabilities,
        'sentiments': sentiments,
        'entity_counts': entity_counter.most_common(10),
        'keywords': keywords
    }

    with open("stats_data.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    return stats


def generate_html_report(stats):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>Stats Report</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 2rem; background: #fdfaf6; color: #1a1a1a; }}
        h1 {{ color: #0a9396; border-bottom: 2px solid #94d2bd; padding-bottom: 0.4rem; }}
        .section {{ margin-bottom: 2rem; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin-bottom: 0.3rem; }}
      </style>
    </head>
    <body>
      <h1>Stats Report</h1>
      <div class="section">
        <strong>Last Updated:</strong> {stats['last_updated']}<br/>
        <strong>Article Count:</strong> {stats['article_count']}<br/>
        <strong>Total Words:</strong> {stats['total_words']}<br/>
        <strong>Average Words per Article:</strong> {stats['avg_words']}<br/>
        <strong>Longest Article:</strong> {stats['longest_article']}<br/>
      </div>
      <div class="section">
        <h2>Top Words</h2>
        <ul>
          {''.join(f"<li>{word}</li>" for word in stats['top_words'])}
        </ul>
      </div>
      <div class="section">
        <h2>Entity Counts (Top 10)</h2>
        <ul>
          {''.join(f"<li>{entity}: {count}</li>" for entity, count in stats['entity_counts'])}
        </ul>
      </div>
    </body>
    </html>
    """
    with open("stats.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    stats = analyze_articles()
    generate_html_report(stats)
