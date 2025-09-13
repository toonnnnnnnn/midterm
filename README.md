# OCR Document Reader

A web application built with FastHTML that performs OCR (Optical Character Recognition) on uploaded images and PDFs using Google's GenAI (Gemini) API.

## Features

- Upload and process images (JPG, PNG) and PDF files
- AI-powered text extraction using Google GenAI
- Clean, responsive web interface
- Docker support for easy deployment

## Setup

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

## Usage

1. Open the web application in your browser
2. Click "Choose a file" and select an image or PDF
3. Click "Extract Text" to process the file
4. View the extracted text on the results page

## API Key

The application uses a pre-configured Google GenAI API key. For production use, consider using environment variables for security.

## Supported File Types

- Images: JPG, JPEG, PNG
- Documents: PDF

## Dependencies

- FastHTML: Web framework
- Google GenAI: AI-powered text extraction
- Pillow: Image processing
- PyMuPDF: PDF processing
