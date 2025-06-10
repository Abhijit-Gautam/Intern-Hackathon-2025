from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
import nltk
import numpy as np
from typing import Dict, List, Any

class EmailSummarizer:
    def __init__(self):
        try:
            # Initialize T5 model for abstractive summarization
            self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
            self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
            
            # Initialize sentence transformer for embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
                
            print("✓ AI models loaded successfully")
        except Exception as e:
            print(f"Warning: Error loading AI models: {str(e)}")
            self.tokenizer = None
            self.model = None
            self.sentence_model = None
    
    def generate_comprehensive_summary(self, email_data: Dict[str, Any], 
                                     extracted_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary of email and extracted documents"""
        
        try:
            # Extract key information with safe handling
            email_summary = self._summarize_email(email_data)
            document_summaries = self._summarize_documents(extracted_docs)
            key_entities = self._extract_entities(email_data, extracted_docs)
            
            # Create comprehensive summary
            comprehensive_summary = {
                'email_metadata': {
                    'sender': self._safe_get_string(email_data.get('sender', '')),
                    'subject': self._safe_get_string(email_data.get('subject', '')),
                    'date': self._safe_get_string(email_data.get('date', '')),
                    'filename': self._safe_get_string(email_data.get('filename', ''))
                },
                'email_summary': email_summary,
                'document_summaries': document_summaries,
                'key_entities': key_entities,
                'total_attachments': len(email_data.get('attachments', [])),
                'processed_documents': len(extracted_docs)
            }
            
            return comprehensive_summary
            
        except Exception as e:
            print(f"Error generating comprehensive summary: {str(e)}")
            # Return a basic summary if AI processing fails
            return self._create_fallback_summary(email_data, extracted_docs)
    
    def _safe_get_string(self, value) -> str:
        """Safely convert any value to string with bounds checking"""
        if value is None:
            return ""
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return str(value[0]) if len(value) > 0 else ""
        else:
            return str(value)
    
    def _summarize_email(self, email_data: Dict[str, Any]) -> str:
        """Generate summary of email content with safe text handling"""
        try:
            subject = self._safe_get_string(email_data.get('subject', ''))
            body = self._safe_get_string(email_data.get('body', ''))
            
            # Create email text with bounds checking
            email_text = f"Subject: {subject}\n\nBody: {body}"
            
            # Ensure we have some content to summarize
            if not email_text.strip() or len(email_text.strip()) < 10:
                return "Email contains minimal content or could not be processed."
            
            # Use AI summarization if models are available
            if self.tokenizer and self.model:
                return self._ai_summarize_text(email_text, max_length=150, min_length=40)
            else:
                return self._fallback_summarize(email_text)
                
        except Exception as e:
            print(f"Error summarizing email: {str(e)}")
            return "Error generating email summary."
    
    def _summarize_documents(self, extracted_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate summaries for extracted documents with safe handling"""
        document_summaries = []
        
        for doc in extracted_docs:
            try:
                extracted_text = self._safe_get_string(doc.get('extracted_text', ''))
                filename = self._safe_get_string(doc.get('filename', 'unknown'))
                content_type = self._safe_get_string(doc.get('content_type', 'unknown'))
                
                if extracted_text and len(extracted_text.strip()) > 10:
                    # Generate summary for document
                    if self.tokenizer and self.model:
                        summary = self._ai_summarize_text(extracted_text, max_length=100, min_length=20)
                    else:
                        summary = self._fallback_summarize(extracted_text)
                else:
                    summary = "Document contains minimal text or could not be processed."
                
                document_summaries.append({
                    'filename': filename,
                    'content_type': content_type,
                    'summary': summary,
                    'word_count': len(extracted_text.split()) if extracted_text else 0
                })
                
            except Exception as e:
                print(f"Error summarizing document {doc.get('filename', 'unknown')}: {str(e)}")
                continue
        
        return document_summaries
    
    def _ai_summarize_text(self, text: str, max_length: int = 150, min_length: int = 40) -> str:
        """Generate AI summary with proper text truncation and bounds checking - FIXED VERSION"""
        try:
            # Safely truncate text to avoid token limits
            max_input_chars = 900  # Conservative limit to avoid tokenization issues
            if len(text) > max_input_chars:
                text = text[:max_input_chars] + "..."
            
            # Prepare input with bounds checking
            input_text = f"summarize: {text}"
            
            # Tokenize with safe parameters
            input_ids = self.tokenizer.encode(
                input_text, 
                return_tensors='pt', 
                max_length=512, 
                truncation=True,
                padding=False
            )
            
            # FIXED: Proper tensor length handling
            input_length = input_ids.shape[1]  # Get actual sequence length
            safe_min_length = min(min_length, max(1, input_length // 3))  # Ensure reasonable min_length
            safe_max_length = max(max_length, input_length + 20)  # Ensure max_length > input_length
            
            # Generate summary with safe parameters
            summary_ids = self.model.generate(
                input_ids,
                max_length=safe_max_length,
                min_length=safe_min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True,
                do_sample=False
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Ensure we return a non-empty summary
            return summary if summary.strip() else self._fallback_summarize(text)
            
        except Exception as e:
            print(f"AI summarization failed: {str(e)}")
            return self._fallback_summarize(text)
    
    def _fallback_summarize(self, text: str) -> str:
        """Simple fallback summarization using first few sentences"""
        try:
            # Safely get first part of text
            if not text or len(text.strip()) < 10:
                return "No meaningful content to summarize."
            
            # Split into sentences and take first few
            sentences = text.split('.')
            if len(sentences) > 0:
                # Take first 2-3 sentences, with bounds checking
                summary_sentences = []
                for i, sentence in enumerate(sentences[:3]):
                    if sentence.strip():
                        summary_sentences.append(sentence.strip())
                    if len(' '.join(summary_sentences)) > 200:
                        break
                
                if summary_sentences:
                    return '. '.join(summary_sentences) + '.'
            
            # If sentence splitting fails, take first 200 characters
            return text[:200].strip() + "..." if len(text) > 200 else text.strip()
            
        except Exception as e:
            print(f"Fallback summarization failed: {str(e)}")
            return "Unable to generate summary."
    
    def _extract_entities(self, email_data: Dict[str, Any], 
                         extracted_docs: List[Dict[str, Any]]) -> List[str]:
        """Extract key entities with safe text handling - FIXED VERSION"""
        try:
            # Safely combine all text
            all_text = ""
            
            body = self._safe_get_string(email_data.get('body', ''))
            if body:
                all_text += body + " "
            
            for doc in extracted_docs:
                doc_text = self._safe_get_string(doc.get('extracted_text', ''))
                if doc_text:
                    all_text += doc_text + " "
            
            if not all_text.strip():
                return ["No entities found"]
            
            # Basic keyword extraction with bounds checking
            words = all_text.lower().split()
            word_freq = {}
            
            for word in words:
                if len(word) > 3 and word.isalpha():
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            if not word_freq:
                return ["No significant keywords found"]
            
            # FIXED: The bug was here - now properly sorting by frequency (x[1])
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10]]
            
        except Exception as e:
            print(f"Error extracting entities: {str(e)}")
            return ["Entity extraction failed"]
    
    def _create_fallback_summary(self, email_data: Dict[str, Any], 
                                extracted_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a basic summary when AI processing fails"""
        return {
            'email_metadata': {
                'sender': self._safe_get_string(email_data.get('sender', '')),
                'subject': self._safe_get_string(email_data.get('subject', '')),
                'date': self._safe_get_string(email_data.get('date', '')),
                'filename': self._safe_get_string(email_data.get('filename', ''))
            },
            'email_summary': "Basic email information extracted (AI processing unavailable)",
            'document_summaries': [
                {
                    'filename': self._safe_get_string(doc.get('filename', 'unknown')),
                    'content_type': self._safe_get_string(doc.get('content_type', 'unknown')),
                    'summary': "Document processed (AI summary unavailable)",
                    'word_count': len(self._safe_get_string(doc.get('extracted_text', '')).split())
                }
                for doc in extracted_docs
            ],
            'key_entities': ["Processing completed with basic extraction"],
            'total_attachments': len(email_data.get('attachments', [])),
            'processed_documents': len(extracted_docs)
        }
