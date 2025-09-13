from fasthtml.common import *
from google.genai import types
from google.genai import Client
import tempfile
import os
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import io
from starlette.datastructures import UploadFile

# Create Google GenAI client
client = Client(api_key="AIzaSyAZGduXRY_l2RCAOdmVJv91cFZKsy0olDg")

# Create FastHTML app
app, rt = fast_app()

def extract_text_from_image(image_data):
    """Extract text from image using Google GenAI"""
    try:
        print("Starting image processing...")
        # Create a PIL Image from bytes
        image = Image.open(io.BytesIO(image_data))
        print(f"Image opened successfully: {image.size}, mode: {image.mode}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print("Converted image to RGB")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            image.save(tmp_file.name, 'JPEG')
            print(f"Saved image to temp file: {tmp_file.name}")
            
            # Read the file and process with GenAI
            with open(tmp_file.name, 'rb') as f:
                image_data = f.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            print("Cleaned up temp file")
            
            # Process with Gemini using the new API - try different approaches
            print("Attempting Google GenAI API call...")
            try:
                # Try with base64 encoding
                import base64
                image_b64 = base64.b64encode(image_data).decode('utf-8')
                print(f"Base64 encoded image, length: {len(image_b64)}")
                
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[
                        "Extract all text from this image. Return only the extracted text without any additional commentary or formatting.",
                        f"data:image/jpeg;base64,{image_b64}"
                    ]
                )
                print("API call successful with base64 method")
                
            except Exception as e1:
                print(f"Base64 method failed: {str(e1)}")
                try:
                    # Try with file path approach
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file2:
                        tmp_file2.write(image_data)
                        tmp_file2.flush()
                        print(f"Created temp file for path method: {tmp_file2.name}")
                        
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[
                                "Extract all text from this image. Return only the extracted text without any additional commentary or formatting.",
                                types.File.from_path(tmp_file2.name)
                            ]
                        )
                        os.unlink(tmp_file2.name)
                        print("API call successful with file path method")
                        
                except Exception as e2:
                    print(f"File path method failed: {str(e2)}")
                    # Fallback to simple text description
                    return "Unable to process image with current API configuration. Please try a different image or check API setup."
            
            result = response.text if response.text else "No text found in the image."
            print(f"OCR result: {result[:100]}...")  # Print first 100 chars
            return result
            
    except Exception as e:
        print(f"Error in extract_text_from_image: {str(e)}")
        return f"Error processing image: {str(e)}"

def extract_text_from_pdf(pdf_data):
    """Extract text from PDF using PyMuPDF and GenAI for images"""
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        extracted_text = []
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # First try to extract text directly
            text = page.get_text()
            if text.strip():
                extracted_text.append(f"Page {page_num + 1}:\n{text}")
            else:
                # If no text, try OCR on the page image
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Use GenAI for OCR
                ocr_text = extract_text_from_image(img_data)
                if ocr_text and ocr_text != "No text found in the image.":
                    extracted_text.append(f"Page {page_num + 1} (OCR):\n{ocr_text}")
        
        pdf_document.close()
        return "\n\n".join(extracted_text) if extracted_text else "No text found in the PDF."
        
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

@rt("/")
def index():
    """Main page with file upload form"""
    return Titled("OCR Document Reader",
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        ),
        Body(
            Div(
                Div(
                    H1("OCR Document Reader", class_="text-center mb-4"),
                    P("Upload an image or PDF file to extract text using AI-powered OCR", class_="text-center text-muted mb-4"),
                    class_="col-md-8 mx-auto"
                ),
                class_="container mt-5"
            ),
            Div(
                Div(
                    Form(
                        Div(
                            Label("Choose a file:", class_="form-label"),
                            Input(type="file", name="file", class_="form-control", accept=".jpg,.jpeg,.png,.pdf", required=True),
                            class_="mb-3"
                        ),
                        Div(
                            Button("Extract Text", type="submit", class_="btn btn-primary btn-lg"),
                            class_="text-center"
                        ),
                        method="post",
                        enctype="multipart/form-data",
                        action="/upload"
                    ),
                    class_="col-md-6 mx-auto"
                ),
                class_="container"
            ),
            Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
        )
    )

@rt("/upload", methods=["POST"])
async def upload_file(request):
    """Handle file upload and OCR processing"""
    try:
        print("Upload request received")
        # Get uploaded file from request
        form = await request.form()
        file = form.get("file")
        print(f"File object: {file}")
        
        # Check if file was uploaded
        if not file or not hasattr(file, 'filename') or not file.filename:
            return Titled("Error",
                Div(
                    Div(
                        H2("Error", class_="text-danger"),
                        P("No file uploaded. Please select a file and try again."),
                        A("← Back to Upload", href="/", class_="btn btn-secondary"),
                        class_="col-md-8 mx-auto text-center"
                    ),
                    class_="container mt-5"
                )
            )
        
        # Read file data
        file_data = await file.read()
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        print(f"File extension: {file_extension}, File size: {len(file_data)} bytes")
        
        # Process based on file type
        if file_extension in ['jpg', 'jpeg', 'png']:
            print("Processing as image...")
            extracted_text = extract_text_from_image(file_data)
        elif file_extension == 'pdf':
            print("Processing as PDF...")
            extracted_text = extract_text_from_pdf(file_data)
        else:
            return Titled("Error",
                Div(
                    Div(
                        H2("Error", class_="text-danger"),
                        P("Unsupported file type. Please upload a JPG, PNG, or PDF file."),
                        A("← Back to Upload", href="/", class_="btn btn-secondary"),
                        class_="col-md-8 mx-auto text-center"
                    ),
                    class_="container mt-5"
                )
            )
        
        # Display results
        return Titled("OCR Results",
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
            ),
            Body(
                Div(
                    Div(
                        H2("Extracted Text", class_="mb-4"),
                        Div(
                            Pre(extracted_text, class_="bg-light p-3 rounded", style="white-space: pre-wrap; max-height: 500px; overflow-y: auto;"),
                            class_="mb-4"
                        ),
                        Div(
                            A("← Upload Another File", href="/", class_="btn btn-primary"),
                            class_="text-center"
                        ),
                        class_="col-md-10 mx-auto"
                    ),
                    class_="container mt-5"
                ),
                Script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
            )
        )
        
    except Exception as e:
        return Titled("Error",
            Div(
                Div(
                    H2("Error", class_="text-danger"),
                    P(f"An error occurred while processing the file: {str(e)}"),
                    A("← Back to Upload", href="/", class_="btn btn-secondary"),
                    class_="col-md-8 mx-auto text-center"
                ),
                class_="container mt-5"
            )
        )

if __name__ == "__main__":
    serve(port=5000)
