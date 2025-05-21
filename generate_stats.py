import os
import re
import spacy
import json
from collections import Counter, defaultdict
from datetime import datetime
from textstat import flesch_reading_ease, flesch_kincaid_grade
from textblob import TextBlob
from wordcloud import WordCloud
from rake_nltk import Rake

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

    print("Scanning articles...")
    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            print(f"  Processing {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                raw_html = f.read()
                # Remove HTML tags for text analysis
                text = re.sub(r'<[^>]+>', ' ', raw_html)
                text_lower = text.lower()
                doc = nlp(text_lower)

                articles.append(filename)
                total_words += len([t for t in doc if t.is_alpha])

                # Word counts and POS counts (alpha tokens only)
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        word_counter[token.text] += 1
                        pos_counters[token.pos_][token.text] += 1

                # Lexical diversity
                words = [t.text for t in doc if t.is_alpha]
                lexical_diversities[filename] = len(set(words)) / len(words) if words else 0

                # Sentence stats (re-parse original text to preserve case and punctuation)
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

                # Sentiment analysis
                blob = TextBlob(text)
                sentiments[filename] = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }

                # Named Entity Recognition (NER)
                doc_ner = nlp(text)
                for ent in doc_ner.ents:
                    entity_counter[ent.label_] += 1

                # Keyword extraction using RAKE with custom stopwords
                rake = Rake(stopwords=STOPWORDS)
                rake.extract_keywords_from_text(text)
                keywords[filename] = rake.get_ranked_phrases()[:10]

                all_text_for_wordcloud.append(text)

    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"

    # Generate word cloud
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


def generate_html(stats):
    pos_html = ""
    for pos, words in stats['pos_summary'].items():
        full_name = POS_FULL_NAMES.get(pos, pos)
        pos_html += f"<p><strong>{full_name}:</strong> {', '.join(words)}</p>"

    lex_html = "<ul>"
    for art, val in stats['lexical_diversities'].items():
        lex_html += f"<li>{art}: {val:.3f}</li>"
    lex_html += "</ul>"

    sent_html = ""
    for art, vals in stats['sentence_stats'].items():
        sent_html += (
            f"<p><strong>{art}:</strong> Avg sentence length: {vals['avg_sentence_length']:.1f}, "
            f"Longest sentence: {vals['longest_sentence_length']}, "
            f"Sentence count: {vals['sentence_count']}</p>"
        )

    read_html = ""
    for art, vals in stats['readabilities'].items():
        read_html += (
            f"<p><strong>{art}:</strong> Flesch Reading Ease: {vals['flesch_reading_ease']:.1f}, "
            f"Flesch-Kincaid Grade: {vals['flesch_kincaid_grade']:.1f}</p>"
        )

    sentim_html = ""
    for art, vals in stats['sentiments'].items():
        sentim_html += (
            f"<p><strong>{art}:</strong> Polarity: {vals['polarity']:.2f}, "
            f"Subjectivity: {vals['subjectivity']:.2f}</p>"
        )

    entity_html = "<ul>"
    for ent, count in stats['entity_counts']:
        entity_html += f"<li>{ent}: {count}</li>"
    entity_html += "</ul>"

    keywords_html = ""
    for art, kw_list in stats['keywords'].items():
        keywords_html += f"<p><strong>{art}:</strong> {', '.join(kw_list)}</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Fun Stats</title>
    <link rel="stylesheet" href="style2.css" />
    <script src="navbar.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>📊 Fun Stats</h1>

    <div class="stats-grid">
        <div class="stat-card">
            <h2>📚 Articles</h2>
            <p>Total: {stats['article_count']}</p>
            <p>Longest: {stats['longest_article']}</p>
        </div>

        <div class="stat-card">
            <h2>📝 Words</h2>
            <p>Total: {stats['total_words']:,}</p>
            <p>Average: {stats['avg_words']:,}/article</p>
        </div>

        <div class="stat-card">
            <h2>🔠 Top Words</h2>
            <ol>{''.join(f'<li>{word}</li>' for word in stats['top_words'])}</ol>
        </div>

        <div class="stat-card">
            <h2>🏷️ Parts of Speech</h2>
            {pos_html}
        </div>

        <div class="stat-card">
            <h2>🧠 Lexical Diversity (Unique words ratio)</h2>
            {lex_html}
        </div>

        <div class="stat-card">
            <h2>✍️ Sentence Stats</h2>
            {sent_html}
        </div>

        <div class="stat-card">
            <h2>📖 Readability</h2>
            {read_html}
        </div>

        <div class="stat-card">
            <h2>🙂 Sentiment</h2>
            {sentim_html}
        </div>

        <div class="stat-card">
            <h2>🏷️ Named Entity Counts</h2>
            {entity_html}
        </div>

        <div class="stat-card">
            <h2>🔑 Keywords per Article</h2>
            {keywords_html}
        </div>

        <div class="stat-card" style="text-align:center;">
            <h2>🌈 Word Cloud</h2>
            <img src="wordcloud.png" alt="Word Cloud" style="max-width: 100%; height: auto;"/>
        </div>
    </div>

    <canvas id="chart" width="400" height="200"></canvas>
    <script>
        const chart = new Chart(document.getElementById('chart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(stats['top_words'])},
                datasets: [{{
                    label: 'Top Words',
                    data: {json.dumps([1] * len(stats['top_words']))},
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    title: {{ display: true, text: 'Top Words Chart' }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html


if __name__ == '__main__':
    stats = analyze_articles()
    with open('stats.html', 'w', encoding='utf-8') as f:
        f.write(generate_html(stats))
    print("✅ Full supercharged stats.html and wordcloud.png generated successfully!")
