import PyPDF2
import docx
from PIL import Image
import io
import pytesseract
from typing import Dict, Any, List

class DocumentExtractor:
    def __init__(self):
        self.extractors = {
            'application/pdf': self._extract_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._extract_docx,
            'image/jpeg': self._extract_image,
            'image/png': self._extract_image,
            'image/jpg': self._extract_image,
            'image/tiff': self._extract_image,
            'text/plain': self._extract_text
        }
    
    def extract_from_attachments(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract content from all attachments"""
        extracted_data = []
        
        for attachment in attachments:
            try:
                content_type = attachment['content_type']
                if content_type in self.extractors:
                    extractor = self.extractors[content_type]
                    extracted_content = extractor(attachment['content'])
                    
                    extracted_data.append({
                        'filename': attachment['filename'],
                        'content_type': content_type,
                        'extracted_text': extracted_content,
                        'metadata': self._extract_metadata(attachment)
                    })
                else:
                    # Try to extract as text if unknown type
                    try:
                        text_content = attachment['content'].decode('utf-8', errors='ignore')
                        if text_content.strip():
                            extracted_data.append({
                                'filename': attachment['filename'],
                                'content_type': content_type,
                                'extracted_text': text_content,
                                'metadata': self._extract_metadata(attachment)
                            })
                    except:
                        print(f"Could not extract content from {attachment['filename']}")
                        
            except Exception as e:
                print(f"Error extracting from {attachment['filename']}: {str(e)}")
                
        return extracted_data
    
    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        text = ""
        pdf_file = io.BytesIO(content)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"PDF extraction error: {str(e)}")
            
        return text.strip()
    
    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        text = ""
        docx_file = io.BytesIO(content)
        
        try:
            doc = docx.Document(docx_file)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {str(e)}")
            
        return text.strip()
    
    def _extract_text(self, content: bytes) -> str:
        """Extract text from plain text files"""
        try:
            return content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            print(f"Text extraction error: {str(e)}")
            return ""
    
    def _extract_image(self, content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Image OCR error: {str(e)}")
            return ""
    
    def _extract_metadata(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from attachment"""
        return {
            'size': len(attachment['content']),
            'type': attachment['content_type']
        }
