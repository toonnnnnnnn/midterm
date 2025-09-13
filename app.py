from fasthtml.common import *
from google.genai import types
import google.genai as genai
import base64
import io
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyAZGduXRY_l2RCAOdmVJv91cFZKsy0olDg")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def process_image_for_ocr(image_data):
    """Process image data for OCR using Gemini API"""
    try:
        # Convert image data to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to bytes for API
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        # Create the prompt for OCR
        prompt = "Extract all text from this image. Return only the extracted text without any additional commentary or formatting."
        
        # Generate content using Gemini
        response = model.generate_content([prompt, types.Part.from_data(img_buffer.getvalue(), mime_type="image/jpeg")])
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_images_from_pdf(pdf_data):
    """Extract images from PDF for OCR processing"""
    try:
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Convert PDF page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            images.append(img_data)
        
        doc.close()
        return images
    except Exception as e:
        raise Exception(f"Error extracting images from PDF: {str(e)}")

def process_pdf_for_ocr(pdf_data):
    """Process PDF for OCR by extracting images and running OCR on each"""
    try:
        images = extract_images_from_pdf(pdf_data)
        all_text = []
        
        for i, img_data in enumerate(images):
            text = process_image_for_ocr(img_data)
            if text and not text.startswith("Error"):
                all_text.append(f"Page {i+1}:\n{text}\n")
        
        return "\n".join(all_text) if all_text else "No text found in PDF"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

# FastHTML routes
@route("/")
def index():
    return Html(
        Head(
            Title("OCR Web Application"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        ),
        Body(
            Div(
                H1("OCR Web Application", class_="text-center mb-4"),
                P("Upload an image or PDF file to extract text using OCR", class_="text-center text-muted mb-4"),
                
                Div(
                    Form(
                        Div(
                            Label("Choose file:", class_="form-label"),
                            Input(type="file", name="file", class_="form-control", accept=".jpg,.jpeg,.png,.pdf", required=True),
                            class_="mb-3"
                        ),
                        Button("Extract Text", type="submit", class_="btn btn-primary"),
                        method="post",
                        enctype="multipart/form-data"
                    ),
                    class_="card p-4 mx-auto",
                    style="max-width: 500px;"
                ),
                
                Div(id="result", class_="mt-4"),
                
                Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
            ),
            class_="container mt-5"
        )
    )

@route("/", methods=["POST"])
def upload_file():
    try:
        # Get uploaded file
        file = request.files.get('file')
        if not file:
            return Html(
                Div(
                    Div(
                        H4("Error", class_="alert-heading"),
                        P("No file uploaded"),
                        class_="alert alert-danger"
                    ),
                    class_="container mt-4"
                )
            )
        
        file_data = file.read()
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        # Process based on file type
        if file_extension in ['jpg', 'jpeg', 'png']:
            result_text = process_image_for_ocr(file_data)
        elif file_extension == 'pdf':
            result_text = process_pdf_for_ocr(file_data)
        else:
            result_text = "Unsupported file type. Please upload JPG, PNG, or PDF files."
        
        # Display result
        return Html(
            Div(
                Div(
                    H4("Extracted Text", class_="alert-heading"),
                    Pre(result_text, class_="mt-3 p-3 bg-light border rounded", style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;"),
                    class_="alert alert-success"
                ),
                Div(
                    A("Upload Another File", href="/", class_="btn btn-secondary")
                ),
                class_="container mt-4"
            )
        )
        
    except Exception as e:
        return Html(
            Div(
                Div(
                    H4("Error", class_="alert-heading"),
                    P(f"An error occurred: {str(e)}"),
                    class_="alert alert-danger"
                ),
                Div(
                    A("Try Again", href="/", class_="btn btn-secondary")
                ),
                class_="container mt-4"
            )
        )

if __name__ == "__main__":
    serve(port=5000)
