from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import re
import shutil
from tempfile import NamedTemporaryFile
from pathlib import Path
from fpdf import FPDF
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
from openai import OpenAI
from PyPDF2 import PdfReader
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from docx import Document

# NLTK veri setini indir
nltk.download("stopwords")
nltk.download("punkt")

# Türkçe stopwords'leri
TURKISH_STOP_WORDS = set(stopwords.words("turkish"))
ENGLISH_STOP_WORDS = set(stopwords.words("english"))
CUSTOM_STOP_WORDS = TURKISH_STOP_WORDS.union(ENGLISH_STOP_WORDS)

# FastAPI uygulamasını başlat
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_openai_client(api_key: str) -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )


def summarize_content(transcript: str, client: OpenAI, model: str = "mistralai/mistral-7b-instruct:free") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": f"This content can be summarized in 1-2 paragraphs maximum: {transcript}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error during summarization: {str(e)}")

# PDF dosyalarından metin çıkarma fonksiyonu
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# PDF dosyasındaki tüm linkleri çıkarma fonksiyonu
def extract_urls_from_pdf(file_path: str) -> list:
    reader = PdfReader(file_path)
    urls = []
    for page in reader.pages:
        text = page.extract_text()
        # URL'leri bulmak için regex kullanın
        url_pattern = r"https?://[^\s]+"
        urls.extend(re.findall(url_pattern, text))
    return urls

# Excel dosyalarından metin çıkarma fonksiyonu
def extract_text_from_excel(file_path: str) -> str:
    try:
        # Excel dosyasını oku
        df = pd.read_excel(file_path)
        # Tüm hücreleri birleştirerek metin oluştur
        text = " ".join(df.astype(str).values.flatten())
        return text
    except Exception as e:
        raise RuntimeError(f"Error reading Excel file: {str(e)}")

# Word dosyalarından metin çıkarma fonksiyonu
def extract_text_from_word(file_path: str) -> str:
    try:
        # Word dosyasını oku
        doc = Document(file_path)
        # Tüm paragrafları birleştirerek metin oluştur
        text = " ".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise RuntimeError(f"Error reading Word file: {str(e)}")


def scrape_content(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return " ".join([p.text for p in soup.find_all("p")])


def fetch_youtube_transcript(video_url: str, language="tr") -> str:
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([entry["text"] for entry in transcript])
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError(f"No transcript found for this video in language: {language}.")
    except Exception as e:
        raise RuntimeError(f"Error fetching transcript: {str(e)}")

def extract_video_id(url: str) -> str:
    pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|\S+\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def tfidf_analysis(text: str, max_words=50, min_score=0.080):
    # TF-IDF vektörleştiriciyi oluştur
    vectorizer = TfidfVectorizer(stop_words=list(CUSTOM_STOP_WORDS))  # Listeye çevirildi
    tfidf_matrix = vectorizer.fit_transform([text])

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    
    filtered_keywords = {feature_names[i]: scores[i] for i in range(len(scores)) if scores[i] >= min_score}
    
    sorted_keywords = dict(sorted(filtered_keywords.items(), key=lambda item: item[1], reverse=True)[:max_words])
    
    return sorted_keywords

def plot_tfidf(tfidf_results, output_file):
    words = list(tfidf_results.keys())
    scores = list(tfidf_results.values())
    plt.figure(figsize=(10, 5))
    plt.barh(words, scores, color="skyblue")
    plt.xlabel("TF-IDF Score")
    plt.ylabel("Keywords")
    plt.title("TF-IDF Keyword Analysis")
    plt.gca().invert_yaxis()
    plt.savefig(output_file)
    plt.close()


def lda_analysis(text, num_topics=50, passes=15):

    tokens = [word for word in simple_preprocess(text) if word not in CUSTOM_STOP_WORDS]

    dictionary = corpora.Dictionary([tokens])
    corpus = [dictionary.doc2bow(tokens)]

    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes)

    topics = []
    for idx, topic in lda_model.print_topics(-1, num_topics):
        topics.append(topic)
    
    return topics


def generate_wordcloud(lda_keywords, output_file):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(lda_keywords))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_file)
    plt.close()


def save_to_pdf(urls: list, summaries: list, tfidf_images: list, lda_images: list, output_pdf: str):
    pdf = FPDF()
    

    font_path = "C:\\Users\\kurt_\\gomulu-isletim-final\\projects\\DejaVuSansCondensed.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"{font_path} font file not found. Please ensure the font file is in the correct location.")
    
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 12)

    for i, url in enumerate(urls):
        pdf.add_page()
        pdf.multi_cell(0, 10, f"URL: {url}\n\n")
        pdf.multi_cell(0, 10, f"Summary:\n{summaries[i]}\n\n")
        pdf.add_page()
        pdf.image(tfidf_images[i], x=10, y=10, w=190)
        pdf.add_page()
        pdf.image(lda_images[i], x=10, y=10, w=190)
    pdf.output(output_pdf)


@app.post("/process-file")
async def process_file(file: UploadFile = File(...)):

    api_key = "sk-or-v1-c03c7b3b90b...." #your-apikey

    file_extension = file.filename.split(".")[-1].lower()
    supported_extensions = ["pdf", "xlsx", "docx"]


    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya türü: {file_extension}. Desteklenen türler: {', '.join(supported_extensions)}"
        )


    with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:

        if file_extension == "pdf":
            urls = extract_urls_from_pdf(temp_file_path)
            content = extract_text_from_pdf(temp_file_path)
        elif file_extension == "xlsx":
            content = extract_text_from_excel(temp_file_path)
            urls = []
        elif file_extension == "docx":
            content = extract_text_from_word(temp_file_path)
            urls = []


        summaries = []
        tfidf_images = []
        lda_images = []

        if file_extension == "pdf":
            for url in urls:

                if "youtube.com" in url or "youtu.be" in url:
                    content = fetch_youtube_transcript(url)
                    summary = summarize_content(content, get_openai_client(api_key))
                else:
                    content = scrape_content(url)
                    summary = summarize_content(content, get_openai_client(api_key))

                summaries.append(summary)


                tfidf_results = tfidf_analysis(content)
                tfidf_path = os.path.join("results", f"tfidf_{urls.index(url)}.png")
                plot_tfidf(tfidf_results, tfidf_path)
                tfidf_images.append(tfidf_path)

                lda_keywords = lda_analysis(content)
                lda_path = os.path.join("results", f"lda_{urls.index(url)}.png")
                generate_wordcloud(lda_keywords, lda_path)
                lda_images.append(lda_path)
        else:

            summary = summarize_content(content, get_openai_client(api_key))
            summaries.append(summary)


            tfidf_results = tfidf_analysis(content)
            tfidf_path = os.path.join("results", "tfidf.png")
            plot_tfidf(tfidf_results, tfidf_path)
            tfidf_images.append(tfidf_path)

            lda_keywords = lda_analysis(content)
            lda_path = os.path.join("results", "lda.png")
            generate_wordcloud(lda_keywords, lda_path)
            lda_images.append(lda_path)

    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(temp_file_path)

    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)


    pdf_path = os.path.join(results_dir, f"{Path(file.filename).stem}_results.pdf")
    save_to_pdf(urls if file_extension == "pdf" else [file.filename], summaries, tfidf_images, lda_images, pdf_path)

    return JSONResponse(content={"result": pdf_path})