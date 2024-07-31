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
email_subject = 'Data Removal Notification'
email_body = 'Your data has been removed from our database.'

# Function to send email
def send_email(recipient_email):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = recipient_email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        print(f'Email sent to {recipient_email}')
    except Exception as e:
        print(f'Failed to send email to {recipient_email}: {e}')

# Function to monitor and check for deleted data
def monitor_deletions():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Query to get current users' IDs and emails
        cursor.execute("SELECT id, email FROM users")
        previous_data = cursor.fetchall()
        previous_ids = set(row[0] for row in previous_data)
        
        while True:
            cursor.execute("SELECT id, email FROM users")
            current_data = cursor.fetchall()
            current_ids = set(row[0] for row in current_data)
            
            deleted_ids = previous_ids - current_ids
            if deleted_ids:
                for row in previous_data:
                    if row[0] in deleted_ids:
                        send_email(row[1])
            
            previous_data = current_data
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
    monitor_deletions()
