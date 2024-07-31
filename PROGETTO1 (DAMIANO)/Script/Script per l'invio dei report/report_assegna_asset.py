import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
email_subject = 'New Asset Assignment'
email_body_template = 'Hello,\n\nYou have been assigned a new asset: {asset_name}.\n\nThis assignment was made on: {timestamp}.\n\nRegards,\nYour Manager'

# Function to send email
def send_email(recipient_email, asset_name, timestamp):
    email_body = email_body_template.format(asset_name=asset_name, timestamp=timestamp)
    
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

# Function to monitor asset assignments
def monitor_asset_assignments():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Initial query to get current assignments
        cursor.execute("SELECT id, name, assigned_to, assigned_timestamp FROM assets WHERE assigned_to IS NOT NULL")
        previous_assignments = cursor.fetchall()
        previous_ids = set(row[0] for row in previous_assignments)
        
        while True:
            cursor.execute("SELECT id, name, assigned_to, assigned_timestamp FROM assets WHERE assigned_to IS NOT NULL")
            current_assignments = cursor.fetchall()
            current_ids = set(row[0] for row in current_assignments)
            
            new_assignments = [row for row in current_assignments if row[0] not in previous_ids]
            if new_assignments:
                for assignment in new_assignments:
                    asset_id, asset_name, assigned_to, assigned_timestamp = assignment
                    send_email(assigned_to, asset_name, assigned_timestamp)
            
            previous_assignments = current_assignments
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
    monitor_asset_assignments()
