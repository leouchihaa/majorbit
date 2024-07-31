import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Database connection configuration
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'database': 'your_database'
}

# Email configuration
smtp_server = 'your_smtp_server'
smtp_port = 587  # or 465 for SSL
smtp_user = 'your_email'
smtp_password = 'your_email_password'
email_subject = 'New Account Created'
email_body_template = 'Hello,\n\nYour account has been added to our system.\n\nUsername: {username}\nEmail: {email}\n\nAccount creation timestamp: {timestamp}.\n\nRegards,\nYour System'

# Function to send email
def send_email(username, email, timestamp):
    email_body = email_body_template.format(username=username, email=email, timestamp=timestamp)
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        print(f'Email sent to {email}')
    except Exception as e:
        print(f'Failed to send email to {email}: {e}')

# Function to monitor new account creations
def monitor_account_creations():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Initial query to get current accounts
        cursor.execute("SELECT id, username, email, created_timestamp FROM accounts")
        previous_accounts = cursor.fetchall()
        previous_ids = set(row[0] for row in previous_accounts)
        
        while True:
            cursor.execute("SELECT id, username, email, created_timestamp FROM accounts")
            current_accounts = cursor.fetchall()
            current_ids = set(row[0] for row in current_accounts)
            
            new_accounts = [row for row in current_accounts if row[0] not in previous_ids]
            if new_accounts:
                for account in new_accounts:
                    account_id, username, email, created_timestamp = account
                    send_email(username, email, created_timestamp)
            
            previous_accounts = current_accounts
            previous_ids = current_ids
            
            # Sleep for a while before next check
            time.sleep(10)  # Adjust the sleep time as needed
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

if __name__ == "__main__":
    monitor_account_creations()
