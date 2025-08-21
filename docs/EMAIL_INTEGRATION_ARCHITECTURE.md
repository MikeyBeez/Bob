# Bob Email Integration Architecture

## Overview
Email integration provides Bob with comprehensive email capabilities including sending, receiving, processing, and managing email communications as part of project workflows.

## Email Tool Categories

### 1. Email Communication Tools
- **Send Email**: Compose and send emails via SMTP
- **Read Email**: Retrieve and process incoming emails via IMAP
- **Email Search**: Find specific emails based on criteria
- **Email Filtering**: Automatic email categorization and processing

### 2. Email Workflow Integration
- **Project Email Management**: Link emails to specific projects
- **Email-to-Task Conversion**: Create jobs from email requests
- **Email Templates**: Professional email templates for common scenarios
- **Email Scheduling**: Send emails at optimal times

### 3. Email Analytics
- **Email Response Tracking**: Monitor email effectiveness
- **Communication Patterns**: Analyze email communication trends
- **Project Communication Health**: Track email-based project communications

## Implementation Architecture

### Core Email Manager
```python
class BobEmailManager:
    """Comprehensive email management for Bob"""
    
    def __init__(self):
        self.smtp_client = SMTPClient()
        self.imap_client = IMAPClient()
        self.email_processor = EmailProcessor()
        self.template_manager = EmailTemplateManager()
        
    # Core functionality
    async def send_email(self, to: List[str], subject: str, body: str) -> bool
    async def get_emails(self, folder: str = "INBOX") -> List[Email]
    async def search_emails(self, criteria: EmailSearchCriteria) -> List[Email]
    async def process_email_for_jobs(self, email: Email) -> List[JobRequest]
```

### Email Configuration
```python
@dataclass
class EmailConfig:
    # SMTP settings (for sending)
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_use_tls: bool = True
    
    # IMAP settings (for receiving)
    imap_server: str
    imap_port: int
    imap_username: str
    imap_use_ssl: bool = True
    
    # Processing settings
    auto_process_emails: bool = True
    email_to_job_conversion: bool = True
    project_email_linking: bool = True
```

### Security Considerations
- **Password Storage**: Email passwords stored in macOS Keychain (same system as API keys)
- **OAuth Integration**: Support for Gmail/Outlook OAuth instead of passwords
- **Encrypted Connections**: TLS/SSL for all email communications
- **Permission Controls**: Clear user consent for email access

## Email Tool Implementation

### 1. SMTP Email Sender
```python
class EmailSenderTool:
    """Professional email sending capabilities"""
    
    async def send_email(self, 
                        to: List[str], 
                        subject: str, 
                        body: str,
                        attachments: List[str] = None,
                        template: str = None) -> EmailResult:
        """Send professional emails with attachments and templates"""
        
    async def send_project_update(self, 
                                 project_name: str,
                                 recipients: List[str],
                                 update_content: str) -> EmailResult:
        """Send formatted project updates"""
        
    async def send_scheduled_email(self,
                                  email_data: EmailData,
                                  send_time: datetime) -> bool:
        """Schedule emails for optimal delivery times"""
```

### 2. IMAP Email Receiver
```python
class EmailReceiverTool:
    """Professional email receiving and processing"""
    
    async def get_new_emails(self, since: datetime = None) -> List[Email]:
        """Retrieve new emails since last check"""
        
    async def search_project_emails(self, project_name: str) -> List[Email]:
        """Find emails related to specific projects"""
        
    async def extract_action_items(self, email: Email) -> List[ActionItem]:
        """Use AI to extract actionable items from emails"""
        
    async def categorize_email(self, email: Email) -> EmailCategory:
        """Automatically categorize emails by type and priority"""
```

### 3. Email-to-Job Processor
```python
class EmailJobProcessor:
    """Convert emails into Bob jobs automatically"""
    
    async def process_request_email(self, email: Email) -> JobRequest:
        """Convert email requests into structured jobs"""
        
    async def detect_email_intent(self, email: Email) -> EmailIntent:
        """Use AI to understand email purpose and required actions"""
        
    async def create_response_job(self, original_email: Email) -> JobRequest:
        """Create job to generate appropriate email response"""
```

## Email Templates System

### Professional Templates
```python
EMAIL_TEMPLATES = {
    "project_update": {
        "subject": "Project Update: {project_name} - {date}",
        "template": """
        Hi {recipient_name},
        
        Here's the latest update on {project_name}:
        
        📊 Progress: {completion_percentage}% complete
        ✅ Completed: {completed_items}
        🔄 In Progress: {in_progress_items}
        📅 Next Milestones: {upcoming_milestones}
        
        {additional_notes}
        
        Best regards,
        Bob AI Assistant
        """
    },
    
    "task_completion": {
        "subject": "Task Completed: {task_name}",
        "template": """
        Hi {recipient_name},
        
        I've completed the task: {task_name}
        
        📋 Summary: {task_summary}
        📁 Results: {results_location}
        ⏱️ Duration: {time_taken}
        💰 Cost: {api_cost}
        
        {results_preview}
        
        Best regards,
        Bob AI Assistant
        """
    },
    
    "error_notification": {
        "subject": "Issue Requiring Attention: {issue_description}",
        "template": """
        Hi {recipient_name},
        
        I encountered an issue that requires your attention:
        
        ⚠️ Issue: {issue_description}
        📍 Component: {affected_component}
        🕐 Time: {error_time}
        🔍 Details: {error_details}
        
        Recommended Actions:
        {recommended_actions}
        
        Best regards,
        Bob AI Assistant
        """
    }
}
```

## Gmail Integration (OAuth)
```python
class GmailIntegration:
    """Professional Gmail integration with OAuth"""
    
    def __init__(self):
        self.oauth_config = {
            "client_id": "stored_in_keychain",
            "client_secret": "stored_in_keychain",
            "scope": ["https://www.googleapis.com/auth/gmail.modify"]
        }
        
    async def authenticate_gmail(self) -> bool:
        """OAuth authentication with Gmail"""
        
    async def send_via_gmail_api(self, email_data: EmailData) -> bool:
        """Send emails via Gmail API"""
        
    async def read_gmail_emails(self, query: str) -> List[Email]:
        """Read emails via Gmail API with advanced search"""
```

## Email Security Implementation

### Secure Credential Management
```python
class EmailCredentialManager:
    """Secure email credential management"""
    
    def store_email_credentials(self, 
                               email_address: str,
                               password: str,
                               server_config: EmailConfig) -> bool:
        """Store email credentials in keychain"""
        service_name = f"ai.bob.email.{email_address}"
        return bob_key_manager.keyring.set_password(service_name, email_address, password)
        
    def get_email_credentials(self, email_address: str) -> Optional[str]:
        """Retrieve email credentials from keychain"""
        service_name = f"ai.bob.email.{email_address}"
        return bob_key_manager.keyring.get_password(service_name, email_address)
```

### Privacy & Consent
```python
class EmailPrivacyManager:
    """Manage email privacy and user consent"""
    
    def request_email_access_permission(self) -> bool:
        """Request explicit user permission for email access"""
        
    def anonymize_email_for_ai_processing(self, email: Email) -> Email:
        """Remove personal information before AI processing"""
        
    def log_email_access(self, operation: str, email_id: str):
        """Log all email access for privacy auditing"""
```

## Integration with Bob's Job System

### Email-Triggered Jobs
```python
# Examples of email-triggered job creation

"Analyze the data in the attachment" 
→ Creates DataAnalysisJob with email attachment

"Schedule a meeting with the team next week"
→ Creates SchedulingJob with calendar integration

"Generate a report on project status"
→ Creates ReportGenerationJob with project context

"Review and summarize these documents"
→ Creates DocumentReviewJob with email attachments
```

### Email Response Automation
```python
class EmailResponseAutomation:
    """Automated email responses for common scenarios"""
    
    async def auto_acknowledge_requests(self, email: Email) -> bool:
        """Send acknowledgment for job requests"""
        
    async def send_completion_notifications(self, job: Job) -> bool:
        """Notify requesters when jobs complete"""
        
    async def send_progress_updates(self, job: Job) -> bool:
        """Send periodic progress updates for long jobs"""
```

## CLI Tools for Email Management

### Email Setup CLI
```bash
# Bob email management commands
python3 tools/manage_email.py setup-gmail       # OAuth setup for Gmail
python3 tools/manage_email.py setup-smtp        # SMTP/IMAP setup
python3 tools/manage_email.py test-connection   # Test email connectivity
python3 tools/manage_email.py list-folders      # List email folders
python3 tools/manage_email.py send-test         # Send test email
```

## Benefits for Bob Users

### Project Management
- **Email-based task assignment**: Send Bob tasks via email
- **Automatic progress updates**: Get project updates via email
- **Team communication**: Bob can participate in email discussions

### Workflow Integration
- **Email-to-job conversion**: Turn email requests into structured work
- **Document processing**: Analyze attachments automatically
- **Response automation**: Bob handles routine email responses

### Professional Communication
- **Template-based emails**: Consistent, professional communication
- **Scheduled sending**: Optimal delivery timing
- **Email analytics**: Track communication effectiveness

This email integration makes Bob a **comprehensive business AI assistant** that can handle email-based workflows professionally and securely!
