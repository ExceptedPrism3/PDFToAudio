import argparse
import io
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import md5
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image
from gtts import gTTS, gTTSError


# Function to save extracted text to a file
def save_text_to_file(text, output_file_path):
    """Save extracted text to a file.

    Args:
        text (str): The text to be saved.
        output_file_path (Path): The path of the file where the text will be saved.
    """
    with open(output_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)


# Function to generate a unique cache key based on text content
def generate_cache_key(text):
    """Generate a MD5 hash for the given text.

    Args:
        text (str): Text to generate a hash for.

    Returns:
        str: MD5 hash of the text.
    """
    return md5(text.encode('utf-8')).hexdigest()


# Function to check if an audio file has already been generated
def is_cached(cache_key, folder_path):
    """Check if an audio file for the given cache key already exists.

    Args:
        cache_key (str): The cache key for the audio file.
        folder_path (Path): The folder where the audio file would be stored.

    Returns:
        bool: True if the audio file exists, False otherwise.
    """
    return (folder_path / f"{cache_key}.mp3").exists()


# Function to convert text to speech
def convert_text_to_speech(text, filename_without_extension, cache_folder_path, language='en', retry_delay=5,
                           max_retries=10):
    """Convert text to speech using Google's Text-to-Speech API.

    Args:
        text (str): Text to be converted to speech.
        filename_without_extension (str): Filename for the output audio file without extension.
        cache_folder_path (Path): Path to the folder where the audio file will be saved.
        language (str, optional): Language for text-to-speech conversion. Defaults to 'en'.
        retry_delay (int, optional): Initial delay in seconds for retrying conversion. Defaults to 5.
        max_retries (int, optional): Maximum number of retries for conversion. Defaults to 10.

    Returns:
        Path: The path to the saved audio file.

    Raises:
        RuntimeError: If conversion fails after maximum retries.
    """
    audio_file_path = cache_folder_path / f"{filename_without_extension}.mp3"

    if audio_file_path.exists():
        print(f"Using existing audio file for {filename_without_extension}")
        return audio_file_path

    for attempt in range(max_retries):
        try:
            tts = gTTS(text, lang=language)
            tts.save(audio_file_path)
            return audio_file_path
        except gTTSError as e:
            if "429 (Too Many Requests)" in str(e):
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
        except Exception as e:
            raise  # Re-raise any other exceptions

    raise RuntimeError("Failed to convert text to speech after retries")


# Function to extract text from PDF using OCR
def extract_text_from_pdf_with_ocr(pdf_path):
    """Extract text from a PDF file using OCR.

    Args:
        pdf_path (Path): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                page_image = page.to_image()
                pil_image = page_image.annotated  # PIL Image object

                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')

                image_bytes = io.BytesIO()
                pil_image.save(image_bytes, format='JPEG')
                image_bytes.seek(0)
                pil_image = Image.open(image_bytes)

                text += pytesseract.image_to_string(pil_image, lang='eng')
    return text


# Main function to process each PDF
def process_pdf(pdf_path, output_folder_path, audio_folder_path, language='en', retry_delay=5, max_retries=10):
    """Process a single PDF file: extract text, convert to speech, and save.

    Args:
        pdf_path (Path): Path to the PDF file.
        output_folder_path (Path): Path to the folder for saving extracted text files.
        audio_folder_path (Path): Path to the folder for saving audio files.
        language (str, optional): Language for text-to-speech conversion. Defaults to 'en'.
        retry_delay (int, optional): Initial delay for retrying conversion. Defaults to 5.
        max_retries (int, optional): Maximum number of retries for conversion. Defaults to 10.
    """
    start_time = time.time()

    filename_without_extension = pdf_path.stem
    text = extract_text_from_pdf_with_ocr(pdf_path)

    if not text.strip():
        print(f"No text found in {pdf_path.name}. Skipping text-to-speech conversion.")
        return

    output_file_path = output_folder_path / f"{filename_without_extension}.txt"
    save_text_to_file(text, output_file_path)

    convert_text_to_speech(text, filename_without_extension, audio_folder_path, language, retry_delay, max_retries)

    end_time = time.time()
    print(f"Processed {pdf_path.name} in {end_time - start_time:.2f} seconds.")


# Entry point for the script
def main():
    """Main function to handle command-line arguments and process PDF files."""
    parser = argparse.ArgumentParser(description="Convert PDF files to audio.")
    parser.add_argument("input_folder", help="Path to the folder containing PDF files")
    parser.add_argument("--output_folder", default=None, help="Path to the folder for saving extracted text files")
    parser.add_argument("--audio_folder", default=None, help="Path to the folder for saving audio files")
    parser.add_argument("--language", default='en', help="Language for text-to-speech conversion")
    parser.add_argument("--parallel", action='store_true', help="Process files in parallel")
    parser.add_argument("--retry_delay", type=int, default=5, help="Initial delay for retrying conversion")
    parser.add_argument("--max_retries", type=int, default=10, help="Maximum retries for conversion")

    args = parser.parse_args()

    script_directory = Path(__file__).parent
    input_folder_path = Path(args.input_folder)
    output_folder_path = Path(args.output_folder) if args.output_folder else script_directory / "output"
    audio_folder_path = Path(args.audio_folder) if args.audio_folder else script_directory / "audio"

    output_folder_path.mkdir(parents=True, exist_ok=True)
    audio_folder_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_folder_path.glob('*.pdf'))

    if args.parallel:
        num_workers = os.cpu_count()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(process_pdf, pdf_path, output_folder_path, audio_folder_path, args.language,
                                       args.retry_delay, args.max_retries) for pdf_path in pdf_files]
            for future in as_completed(futures):
                future.result()
    else:
        for pdf_path in pdf_files:
            process_pdf(pdf_path, output_folder_path, audio_folder_path, args.language, args.retry_delay,
                        args.max_retries)


if __name__ == "__main__":
    main()
