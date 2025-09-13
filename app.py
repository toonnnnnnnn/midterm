from fasthtml import *
import google.generativeai as genai
import os
import tempfile
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import io

# Configure Google GenAI
genai.configure(api_key="AIzaSyAZGduXRY_l2RCAOdmVJv91cFZKsy0olDg")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_image(image_path):
    """Extract text from image using Google GenAI"""
    try:
        image = Image.open(image_path)
        response = model.generate_content(["Extract all text from this image. Return only the extracted text without any additional commentary.", image])
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF by converting pages to images and using OCR"""
    try:
        doc = fitz.open(pdf_path)
        extracted_text = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Convert page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Save temporary image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(img_data)
                tmp_file.flush()
                
                # Extract text from image
                text = extract_text_from_image(tmp_file.name)
                extracted_text.append(f"Page {page_num + 1}:\n{text}\n")
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
        
        doc.close()
        return "\n".join(extracted_text)
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

@get("/")
def index():
    return html(
        head(
            title("OCR Web Application"),
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        ),
        body(
            div(class_="container mt-5",
                div(class_="row justify-content-center",
                    div(class_="col-md-8",
                        div(class_="card",
                            div(class_="card-header bg-primary text-white",
                                h1(class_="card-title text-center mb-0", "OCR Text Extraction")
                            ),
                            div(class_="card-body",
                                form(action="/upload", method="post", enctype="multipart/form-data",
                                    div(class_="mb-3",
                                        label(for_="file", class_="form-label", "Select Image or PDF File:"),
                                        input(type="file", class_="form-control", id_="file", name="file", accept=".jpg,.jpeg,.png,.pdf", required=True)
                                    ),
                                    div(class_="d-grid",
                                        button(type="submit", class_="btn btn-primary btn-lg", "Extract Text")
                                    )
                                ),
                                div(id="result", class_="mt-4")
                            )
                        )
                    )
                )
            ),
            script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
        )
    )

@post("/upload")
def upload_file(file: UploadFile):
    if not file:
        return html(
            div(class_="alert alert-danger", "No file uploaded!"),
            script("document.getElementById('result').innerHTML = arguments[0].outerHTML;", div(class_="alert alert-danger", "No file uploaded!"))
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = file.file.read()
            tmp_file.write(content)
            tmp_file.flush()
            
            # Determine file type and extract text
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png']:
                extracted_text = extract_text_from_image(tmp_file.name)
            elif file_extension == '.pdf':
                extracted_text = extract_text_from_pdf(tmp_file.name)
            else:
                extracted_text = "Unsupported file format. Please upload JPG, PNG, or PDF files."
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Return result
            result_html = div(
                div(class_="alert alert-success", f"Successfully processed: {file.filename}"),
                div(class_="card mt-3",
                    div(class_="card-header", "Extracted Text:"),
                    div(class_="card-body",
                        pre(class_="bg-light p-3", style="max-height: 400px; overflow-y: auto;", extracted_text)
                    )
                )
            )
            
            return html(
                script(f"document.getElementById('result').innerHTML = `{result_html}`;")
            )
            
    except Exception as e:
        error_html = div(class_="alert alert-danger", f"Error processing file: {str(e)}")
        return html(
            script(f"document.getElementById('result').innerHTML = `{error_html}`;")
        )

if __name__ == "__main__":
    serve(port=5000)
