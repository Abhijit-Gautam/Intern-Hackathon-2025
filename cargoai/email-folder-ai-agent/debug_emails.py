# debug_email.py
import mailparser

def debug_email(file_path):
    print(f"Debugging: {file_path}")
    
    try:
        mail = mailparser.parse_from_file(file_path)
        
        print(f"From: {type(mail.from_)} - {mail.from_}")
        print(f"To: {type(mail.to)} - {mail.to}")
        print(f"Subject: {type(mail.subject)} - {mail.subject}")
        print(f"Date: {type(mail.date)} - {mail.date}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_email('emails/sample.eml')
    debug_email('emails/newsletter.eml')
