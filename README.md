# OCR Web Application

A web application built with FastHTML and Google GenAI for extracting text from images and PDFs using OCR (Optical Character Recognition).

## Features

- Upload images (JPG, PNG) or PDF files
- Extract text using Google's Gemini AI model
- Modern, responsive web interface
- Docker support for easy deployment

## Requirements

- Python 3.11+
- Google GenAI API key (already configured in the application)

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t ocr-app .
```

2. Run the container:
```bash
docker run -p 5000:5000 ocr-app
```

The application will be available at `http://localhost:5000`

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Click "Choose File" and select an image (JPG, PNG) or PDF file
3. Click "Extract Text" to process the file
4. View the extracted text in the results section

## API Endpoints

- `GET /` - Main application interface
- `POST /upload` - File upload and OCR processing endpoint

## Dependencies

- `fasthtml` - Fast web framework
- `google-generativeai` - Google GenAI library
- `Pillow` - Image processing
- `PyMuPDF` - PDF processing
- `python-multipart` - File upload handling

## Notes

- The application uses Google's Gemini 1.5 Flash model for OCR
- PDF files are converted to images page by page for text extraction
- Temporary files are automatically cleaned up after processing
