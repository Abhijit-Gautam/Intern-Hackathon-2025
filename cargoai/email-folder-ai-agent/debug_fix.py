# debug_fix.py
import os
import sys
import traceback

# Add src to path
sys.path.insert(0, 'src')

def test_parsing():
    """Test email parsing separately"""
    from email_parser import EmailParser
    
    print("=== Testing Email Parsing ===")
    parser = EmailParser()
    emails = parser.parse_email_folder('emails')
    
    for email in emails:
        print(f"\nParsed: {email['filename']}")
        print(f"  Sender: {email['sender'][:50]}...")
        print(f"  Subject: {email['subject'][:50]}...")
        print(f"  Body length: {len(email['body'])}")
        print(f"  Body preview: {email['body'][:100]}...")
        print(f"  Attachments: {len(email['attachments'])}")
    
    return emails

def test_summarization(emails):
    """Test summarization separately"""
    from document_extractor import DocumentExtractor
    from summarizer import EmailSummarizer
    
    print("\n=== Testing Summarization ===")
    
    if not emails:
        print("No emails to test!")
        return
    
    email_data = emails[0]  # Test first email
    print(f"Testing email: {email_data['filename']}")
    
    try:
        # Test document extraction
        doc_extractor = DocumentExtractor()
        extracted_docs = doc_extractor.extract_from_attachments(email_data['attachments'])
        print(f"  Extracted {len(extracted_docs)} documents")
        
        # Test summarizer initialization
        summarizer = EmailSummarizer()
        print("  Summarizer initialized")
        
        # Test individual components
        print("  Testing email summary...")
        email_summary = summarizer._summarize_email(email_data)
        print(f"    Email summary: {email_summary[:100]}...")
        
        print("  Testing document summaries...")
        doc_summaries = summarizer._summarize_documents(extracted_docs)
        print(f"    Document summaries: {len(doc_summaries)}")
        
        print("  Testing entity extraction...")
        entities = summarizer._extract_entities(email_data, extracted_docs)
        print(f"    Entities: {entities}")
        
        print("  Testing comprehensive summary...")
        summary = summarizer.generate_comprehensive_summary(email_data, extracted_docs)
        print("  ✓ Summary generated successfully!")
        
        return summary
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        traceback.print_exc()
        return None

def main():
    # Test parsing
    emails = test_parsing()
    
    # Test summarization
    if emails:
        summary = test_summarization(emails)
        if summary:
            print("\n=== SUCCESS ===")
            print("All components working correctly!")
        else:
            print("\n=== FAILED ===")
            print("Summarization failed!")
    else:
        print("\n=== NO DATA ===")
        print("No emails found to process!")

if __name__ == "__main__":
    main()

