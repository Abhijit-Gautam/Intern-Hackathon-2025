import os
import json
from typing import List, Dict, Any
from email_parser import EmailParser
from document_extractor import DocumentExtractor
from summarizer import EmailSummarizer

class EmailProcessingAgent:
    def __init__(self, email_folder: str, output_folder: str):
        self.email_folder = email_folder
        self.output_folder = output_folder
        self.email_parser = EmailParser()
        self.document_extractor = DocumentExtractor()
        self.summarizer = EmailSummarizer()
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
    
    def process_all_emails(self) -> List[Dict[str, Any]]:
        """Process all emails in the folder and generate summaries"""
        print("Starting email processing...")
        
        # Parse all emails
        emails = self.email_parser.parse_email_folder(self.email_folder)
        print(f"Found {len(emails)} emails to process")
        
        processed_results = []
        
        for i, email_data in enumerate(emails, 1):
            print(f"Processing email {i}/{len(emails)}: {email_data['filename']}")
            
            try:
                # Extract content from attachments
                extracted_docs = self.document_extractor.extract_from_attachments(
                    email_data['attachments']
                )
                
                # Generate comprehensive summary
                summary = self.summarizer.generate_comprehensive_summary(
                    email_data, extracted_docs
                )
                
                # Save individual summary
                output_filename = f"summary_{email_data['filename']}.json"
                output_path = os.path.join(self.output_folder, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                
                processed_results.append({
                    'email_filename': email_data['filename'],
                    'summary': summary,
                    'output_file': output_filename
                })
                
                print(f"✓ Processed: {email_data['filename']}")
                
            except Exception as e:
                print(f"✗ Error processing {email_data['filename']}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Save comprehensive results
        results_path = os.path.join(self.output_folder, 'processing_results.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(processed_results, f, indent=2, ensure_ascii=False)
        
        print(f"Processing complete! Results saved to {self.output_folder}")
        return processed_results

def main():
    """Main function to run the email processing agent"""
    email_folder = "emails"
    output_folder = "output"
    
    # Create folders if they don't exist
    os.makedirs(email_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize and run the agent
    agent = EmailProcessingAgent(email_folder, output_folder)
    results = agent.process_all_emails()
    
    print(f"\n=== Processing Summary ===")
    print(f"Total emails processed: {len(results)}")
    print(f"Results saved in: {output_folder}")

if __name__ == "__main__":
    main()
