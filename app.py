from flask import Flask,render_template ,request ,send_file
import fitz
import os , pyttsx3
from fpdf import FPDF

app = Flask(__name__)

#===============================================--PDF_TO_Audio--==============================================================
OUTPUT_DIR = "audio_files"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
pdf_DIR = "pdf_files"
if not os.path.exists(pdf_DIR):
    os.makedirs(pdf_DIR)

# Extracting Text from PDF // PDF ===> __TEXT__
def pdf_to_text(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

    except Exception as e:
        print(f"Error processing PDF: {e}")
    return text

def text_to_audio(text, audio_path):
    speaker = pyttsx3.init()
    speaker.save_to_file(text, audio_path)
    speaker.runAndWait()
#===============================================--Speech_to_PDF--=============================================================

def text_to_pdf(text,file_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    output_filepath = os.path.join(pdf_DIR, f"{file_name[:10]}.pdf")
    pdf.output(output_filepath)
    return output_filepath
    
#===============================================--MAIN--=============================================================

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/pdf_to_audio', methods=['GET', 'POST'])
def pdf_to_audio():
    # Ensure you're rendering the correct HTML template
    if request.method == 'POST':
        file = request.files.get('file')

        if file is None or file.filename == '':
            return "No file part", 400
        
        file_path = os.path.join(pdf_DIR, file.filename)
        file.save(file_path)

        # Process the uploaded file to extract text
        text = pdf_to_text(file_path) 

        # Convert the extracted text to audio
        audio_filename = f"{file.filename.rsplit('.', 1)[0]}.mp3" #To get audio file name
        audio_path = os.path.join(OUTPUT_DIR, audio_filename)  #for Path
        text_to_audio(text, audio_path) 

        return send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype="audio/mpeg")
    
    # Ensure you're rendering the correct HTML template
    # if request.method == 'POST':
    #     # Check if the file part exists
    #     file = request.files.get('file')
        

    #     if file is None or file.filename == '':
    #         return "No file part", 400  # Return an error message if no file is selected
        
    #     with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
    #             file.save(temp_file.name)
    #             # Process the uploaded file to extract text
    #             text = pdf_to_text(temp_file.name)

    #             if not text.strip():
    #                 return "No text found in the PDF", 400  # Handle case with no text extracted

    #             # Convert the extracted text to audio
    #             audio_filename = f"{file.filename.rsplit('.', 1)[0]}.mp3"
    #             audio_path = os.path.join(OUTPUT_DIR, audio_filename)
    #             text_to_audio(text, audio_path)
                
    #             # Return the audio file to the user
    #             return send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype="audio/mpeg")
    

    # For GET requests, render the form
    return render_template('pdf_to_audio.html')

@app.route('/speech_to_pdf', methods=['GET', 'POST'])
def speech_to_pdf():  
    if request.method == 'POST':  
        text = request.form.get('text')
        file_name = text[:10]
        
        pdf_filepath = text_to_pdf(text, file_name)
        return send_file(pdf_filepath, as_attachment=True, download_name=f"{file_name}.pdf", mimetype="application/pdf")

    return render_template('speech_to_pdf.html')
   

if __name__ == "__main__":
    app.run(debug=True)
