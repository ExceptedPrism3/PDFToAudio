# PDF To Audio

Convert your PDF documents into audio files effortlessly with `PDF to Audio Converter`.
This Python script harnesses the power of Optical Character Recognition (OCR) and Google's Text-to-Speech (gTTS) service
to transform written content into spoken words. Ideal for accessibility, auditory learning, or enjoying documents on-the-go.

## 🌟 Features

- **PDF Text Extraction**: Utilizes `pdfplumber` for precise text extraction.
- **OCR Capability**: Integrates `pytesseract` for handling image-based PDFs.
- **Text-to-Speech**: Leverages Google's gTTS API for high-quality audio output.
- **Parallel Processing**: Option for faster processing of multiple documents.
- **Rate Limit Management**: Smart retry logic with exponential backoff.
- **Flexible CLI**: Command-line interface for customizable configurations.

## 📋 Installation

Get started with these simple steps:

### Prerequisites

- Python 3.x
- Required packages: `pdfplumber`, `pytesseract`, `Pillow`, `gtts`

### Install Python Packages

```bash
pip install pdfplumber pytesseract Pillow gtts
```

## Tesseract OCR
pytesseract requires Tesseract OCR. Install it from [Tesseract's GitHub page](https://github.com/tesseract-ocr/tesseract#installing-tesseract).

## 🚀 Usage

## Command Syntax

```bash
python main.py <input_folder> [--output_folder OUTPUT_FOLDER] [--audio_folder AUDIO_FOLDER] [options]
```

### Arguments

- input_folder: Folder containing PDF files.
- output_folder (optional): Folder for saving text files (defaults to script directory).
- audio_folder (optional): Folder for saving audio files (defaults to script directory).

### Options

- --language: Language for conversion (default: 'en').
- --parallel: Enable parallel processing (sequential by default).
- --retry_delay: Delay in seconds for retrying conversion (default: 5).
- --max_retries: Max retries for conversion (default: 10).

## Example

```bash
python main.py ./pdfs --output_folder ./texts --audio_folder ./audios --language fr --parallel --retry_delay 2 --max_retries 3
```

Processes PDFs in ./pdfs, saves text to ./texts, audio to ./audios, in French, with parallel processing,
a 2-second retry delay, and a maximum of 3 retries.

## 🤝 Contributing

Your contributions are welcome! Feel free to submit bug fixes, feature requests, or documentation improvements.
Check out the issues and pull requests sections.

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.
