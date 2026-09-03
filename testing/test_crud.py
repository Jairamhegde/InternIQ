import os
from backend.crud import(
    extract_docx, extract_pdf, analyze_gap
)

def test_extract_docs():
    docx_path = os.path.join(os.path.dirname(__file__), "test_resume.docx")
    with open(docx_path, "rb") as f:
        text = extract_docx(f)
    
    assert "Java" in text
    assert "React" in text

def test_extract_pdf():
    pdf_path = os.path.join(os.path.dirname(__file__), "test_resume.pdf")
    with open(pdf_path, "rb") as f:
        text = extract_pdf(f)
    
    assert "Python" in text
    assert "Django" in text




if __name__ == '__main__':
    print("Running tests...")
    
    test_extract_docs()
    print(" DOCX extraction passed!")
    
    test_extract_pdf()
    print("PDF extraction passed!")
    
    print("All tests passed successfully!")


    

