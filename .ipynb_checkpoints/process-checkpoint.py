import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from gensim import corpora, models
from matplotlib import pyplot as plt
from fpdf import FPDF
import os
import re
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Veri kümelerini kontrol et
nltk.download('stopwords')

# İngilizce durak kelimeler
ENGLISH_STOP_WORDS = set(stopwords.words('english'))

# OpenRouter API client setup
def get_openai_client(api_key):
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

# Summarization function using OpenRouter API
def summarize_content(transcript, client, model="mistralai/mistral-7b-instruct:free"):
    try:
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "your_site_url_here",
                "X-Title": "Your App Name Here"
            },
            model=model,
            messages=[
                {"role": "user", "content": f"This content can be summarized in 1-2 paragraphs maximum: {transcript}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error during summarization: {str(e)}")

# Web scraping function
def scrape_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])

# Extract YouTube video ID
def extract_video_id(url):
    pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|\S+\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

# Fetch YouTube transcript
def fetch_youtube_transcript(video_url, language="en"):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([entry['text'] for entry in transcript])
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript found for this video.")
    except Exception as e:
        raise RuntimeError(f"Error fetching transcript: {str(e)}")

# TF-IDF analysis function
def tfidf_analysis(text, max_words=200, min_score=0.1):
    vectorizer = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    # Filter keywords with a minimum score
    filtered_keywords = {feature_names[i]: scores[i] for i in range(len(scores)) if scores[i] >= min_score}

    # Sort keywords by score in descending order
    sorted_keywords = dict(sorted(filtered_keywords.items(), key=lambda item: item[1], reverse=True)[:max_words])

    return sorted_keywords

# Plot TF-IDF results
def plot_tfidf(tfidf_results, output_file):
    words = list(tfidf_results.keys())
    scores = list(tfidf_results.values())

    plt.figure(figsize=(10, 5))
    plt.barh(words, scores, color='skyblue')
    plt.xlabel('TF-IDF Score')
    plt.ylabel('Keywords')
    plt.title('TF-IDF Keyword Analysis')
    plt.gca().invert_yaxis()  # Invert y-axis for better visualization
    plt.savefig(output_file)
    plt.close()

# LDA analysis function
def lda_analysis(text, num_topics=200):
    tokenizer = RegexpTokenizer(r'\b\w+\b')
    tokens = [word for word in tokenizer.tokenize(text.lower()) if word.isalnum() and word not in ENGLISH_STOP_WORDS]
    dictionary = corpora.Dictionary([tokens])
    corpus = [dictionary.doc2bow(tokens)]
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

    # Extract top words for the topics with unique keywords
    unique_words = set()
    topics = []
    for i in range(num_topics):
        topic_keywords = [word for word, _ in lda_model.show_topic(i) if word not in unique_words]
        unique_words.update(topic_keywords)
        topics.append(' '.join(topic_keywords))
    return topics

# Generate WordCloud from LDA
def generate_wordcloud(lda_keywords, output_file):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(lda_keywords))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(output_file)
    plt.close()

# Save results to PDF
def save_to_pdf(url, summary, tfidf_image, lda_image, output_pdf):
    pdf = FPDF()
    pdf.add_page()

    # Unicode font ekle
    font_path = r"C:\Users\kurt_\gomulu-isletim-final\projects\DejaVuSansCondensed.ttf"

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"{font_path} font file not found. Please download and place it in the current directory.")

    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 12)

    pdf.multi_cell(0, 10, f"URL: {url}\n\n")
    pdf.multi_cell(0, 10, f"Summary:\n{summary}\n\n")

    pdf.add_page()
    pdf.image(tfidf_image, x=10, y=10, w=190)

    pdf.add_page()
    pdf.image(lda_image, x=10, y=10, w=190)
    pdf.output(output_pdf)


# Main function to process a URL
def process_url(url, api_key, output_folder="results"):
    os.makedirs(output_folder, exist_ok=True)
    client = get_openai_client(api_key)

    print("Scraping content or fetching transcript...")
    if "youtube.com" in url or "youtu.be" in url:
        content = fetch_youtube_transcript(url)
    else:
        content = scrape_content(url)

    print("Summarizing content...")
    summary = summarize_content(content, client)

    print("Performing TF-IDF analysis...")
    tfidf_results = tfidf_analysis(content)
    tfidf_image_path = os.path.join(output_folder, "tfidf_plot.png")

    print("Generating TF-IDF plot...")
    plot_tfidf(tfidf_results, tfidf_image_path)

    print("Performing LDA analysis...")
    lda_keywords = lda_analysis(content)
    lda_image_path = os.path.join(output_folder, "lda_wordcloud.png")

    print("Generating word cloud...")
    generate_wordcloud(lda_keywords, lda_image_path)

    output_pdf = os.path.join(output_folder, "results.pdf")
    print("Saving results to PDF...")
    save_to_pdf(url, summary, tfidf_image_path, lda_image_path, output_pdf)

    print(f"Processing complete. Results saved to {output_pdf}")

# Example usage
if __name__ == "__main__":
    example_url = "https://medium.com/@NvidiaAI/enterprise-ai-with-gpu-integrated-infrastructure-3fefab028452"
    api_key = os.getenv("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")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
    process_url(example_url, api_key)
