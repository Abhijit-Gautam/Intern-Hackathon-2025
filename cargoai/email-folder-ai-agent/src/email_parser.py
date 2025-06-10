import mailparser
import os
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any

class EmailParser:
    def __init__(self):
        self.supported_formats = ['.eml', '.msg']
    
    def parse_email_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Parse all emails in the specified folder"""
        emails = []
        
        if not os.path.exists(folder_path):
            print(f"Email folder {folder_path} does not exist. Creating it...")
            os.makedirs(folder_path, exist_ok=True)
            return emails
        
        for filename in os.listdir(folder_path):
            if any(filename.endswith(fmt) for fmt in self.supported_formats):
                email_path = os.path.join(folder_path, filename)
                try:
                    parsed_email = self.parse_single_email(email_path)
                    if parsed_email:
                        emails.append(parsed_email)
                        print(f"✓ Successfully parsed: {filename}")
                except Exception as e:
                    print(f"✗ Error parsing {filename}: {str(e)}")
                    
        return emails
    
    def parse_single_email(self, email_path: str) -> Dict[str, Any]:
        """Parse a single email file using mail-parser"""
        filename = os.path.basename(email_path)
        
        try:
            # Parse the email file
            mail = mailparser.parse_from_file(email_path)
            
            # Extract email data with proper type handling
            email_data = {
                'sender': self._safe_get_string(mail.from_),
                'subject': self._safe_get_string(mail.subject),
                'date': self._safe_get_string(mail.date),
                'to': self._safe_get_email_list(mail.to),
                'cc': self._safe_get_email_list(mail.cc),
                'body': self._extract_body(mail),
                'attachments': self._extract_attachments(mail),
                'filename': filename
            }
            
            return email_data
            
        except Exception as e:
            print(f"Error parsing {filename}: {str(e)}")
            # Try fallback method with built-in email parser
            return self._fallback_parse(email_path)
    
    def _safe_get_string(self, value) -> str:
        """Safely convert any value to string"""
        if value is None:
            return ""
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            # Handle case where value is a list/tuple of strings
            return str(value[0]) if len(value) > 0 else ""
        else:
            return str(value)
    
    def _safe_get_email_list(self, email_list) -> str:
        """Safely extract email addresses from various formats - FIXED VERSION"""
        if not email_list:
            return ""
        
        if isinstance(email_list, str):
            return email_list
        elif isinstance(email_list, (list, tuple)):
            # Handle list/tuple of email addresses
            result = []
            for email in email_list:
                if isinstance(email, tuple):
                    # Extract email from tuple (name, email) format
                    if len(email) >= 2:
                        result.append(str(email[1]))  # Get email part
                    elif len(email) == 1:
                        result.append(str(email[0]))
                    else:
                        # Handle empty tuples safely
                        result.append("unknown_email")
                else:
                    result.append(str(email))
            return ', '.join(result)
        else:
            return str(email_list)
    
    def _extract_body(self, mail) -> str:
        """Extract email body text from mail-parser object with proper HTML handling"""
        body_parts = []
        
        try:
            # Get plain text body first
            if hasattr(mail, 'text_plain') and mail.text_plain:
                for part in mail.text_plain:
                    if isinstance(part, str) and part.strip():
                        body_parts.append(part.strip())
            
            # If no plain text, get HTML body and convert to clean text
            elif hasattr(mail, 'text_html') and mail.text_html:
                for html_part in mail.text_html:
                    if isinstance(html_part, str):
                        clean_text = self._html_to_clean_text(html_part)
                        if clean_text:
                            body_parts.append(clean_text)
            
            # Fallback to general body
            elif hasattr(mail, 'body') and mail.body:
                body_text = str(mail.body)
                # Check if it's HTML and convert
                if self._is_html(body_text):
                    clean_text = self._html_to_clean_text(body_text)
                    body_parts.append(clean_text)
                else:
                    body_parts.append(body_text)
        
        except Exception as e:
            print(f"Error extracting body: {str(e)}")
            body_parts.append("Error extracting email body")
        
        return '\n\n'.join(body_parts).strip()
    
    def _html_to_clean_text(self, html_content: str) -> str:
        """Convert HTML content to clean, readable text"""
        try:
            # Use BeautifulSoup to parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"Error converting HTML to text: {str(e)}")
            # Fallback: remove HTML tags with regex
            return self._strip_html_tags(html_content)
    
    def _strip_html_tags(self, html_content: str) -> str:
        """Fallback method to strip HTML tags using regex"""
        try:
            # Remove HTML tags
            clean = re.compile('<.*?>')
            text = re.sub(clean, '', html_content)
            
            # Clean up common HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return text
        except:
            return html_content
    
    def _is_html(self, text: str) -> bool:
        """Check if text contains HTML markup"""
        return bool(re.search(r'<[^>]+>', text))
    
    def _extract_attachments(self, mail) -> List[Dict[str, Any]]:
        """Extract attachments from mail-parser object"""
        attachments = []
        
        try:
            if hasattr(mail, 'attachments') and mail.attachments:
                for attachment in mail.attachments:
                    if isinstance(attachment, dict):
                        filename = attachment.get('filename', 'unknown_attachment')
                        content_type = attachment.get('mail_content_type', 'application/octet-stream')
                        
                        # Get binary content
                        import base64
                        payload = attachment.get('payload', '')
                        if payload:
                            try:
                                content = base64.b64decode(payload)
                            except:
                                content = payload.encode() if isinstance(payload, str) else payload
                        else:
                            content = b''
                        
                        attachments.append({
                            'filename': filename,
                            'content': content,
                            'content_type': content_type
                        })
        
        except Exception as e:
            print(f"Error extracting attachments: {str(e)}")
        
        return attachments
    
    def _fallback_parse(self, email_path: str) -> Dict[str, Any]:
        """Fallback parser using Python's built-in email library"""
        import email
        
        try:
            with open(email_path, 'rb') as f:
                msg = email.message_from_bytes(f.read())
            
            email_data = {
                'sender': msg.get('From', ''),
                'subject': msg.get('Subject', ''),
                'date': msg.get('Date', ''),
                'to': msg.get('To', ''),
                'cc': msg.get('Cc', ''),
                'body': self._extract_body_builtin(msg),
                'attachments': self._extract_attachments_builtin(msg),
                'filename': os.path.basename(email_path)
            }
            
            return email_data
        except Exception as e:
            print(f"Fallback parsing also failed: {str(e)}")
            return None
    
    def _extract_body_builtin(self, msg) -> str:
        """Extract email body using built-in parser"""
        body = ""
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_content = payload.decode('utf-8', errors='ignore')
                            # Convert HTML to clean text
                            clean_text = self._html_to_clean_text(html_content)
                            body += clean_text
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
                    if self._is_html(content):
                        body = self._html_to_clean_text(content)
                    else:
                        body = content
        except Exception as e:
            print(f"Error in builtin body extraction: {str(e)}")
            body = "Error extracting email body"
            
        return body.strip()
    
    def _extract_attachments_builtin(self, msg) -> List[Dict[str, Any]]:
        """Extract attachments using built-in parser"""
        attachments = []
        
        try:
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        content = part.get_payload(decode=True)
                        if content:
                            attachments.append({
                                'filename': filename,
                                'content': content,
                                'content_type': part.get_content_type() or 'application/octet-stream'
                            })
        except Exception as e:
            print(f"Error extracting attachments (builtin): {str(e)}")
                    
        return attachments
