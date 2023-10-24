import os
import base64
from typing import List
import datetime
import io
from PyPDF2 import PdfReader
from google_apis import create_service
import re


CLIENT_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
service = create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)


class GmailException(Exception):
	"""gmail base exception class"""


class NoEmailFound(GmailException):
	"""no email found"""


def search_emails(query: str, label_ids: List = None):
	try:
		message_list_response = service.users().messages().list(
			userId='me',
			labelIds=label_ids,
			q=query
		).execute()

		message_items = message_list_response.get('messages')
		next_page_token = message_list_response.get('nextPageToken')
		
		while next_page_token:
			message_list_response = service.users().messages().list(
				userId='me',
				labelIds=label_ids,
				q=query,
				pageToken=next_page_token
			).execute()

			message_items.extend(message_list_response.get('messages'))
			next_page_token = message_list_response.get('nextPageToken')
		return message_items
	except Exception as e:
		raise NoEmailFound('No emails returned')


def get_message_detail(message_id, msg_format='metadata', metadata_headers: List = None):
	message_detail = service.users().messages().get(
		userId='me',
		id=message_id,
		format=msg_format,
		metadataHeaders=metadata_headers
	).execute()
	return message_detail


def initiate_download():
	query_string = 'is:unread AND has:attachment'

	save_location = os.getcwd()
	email_messages = search_emails(query_string)
	if email_messages is None:
		print('No new data. End')
		exit(0)
	for msg in email_messages:
		msg_id = msg['id']

		# Get message date
		msg_date = service.users().messages().get(userId='me', id=msg_id).execute()['internalDate']
		date = datetime.datetime.fromtimestamp(int(msg_date) / 1000)
		date_str = date.strftime("%d-%m-%Y")

		message = service.users().messages().get(userId='me', id=msg_id).execute()

		for part in message['payload']['parts']:
			if part['filename'] and part['body']['attachmentId']:
				attach_id = part['body']['attachmentId']
				name = part['filename']
				request = service.users().messages().attachments().get(
					userId='me', messageId=msg_id, id=attach_id)
				file_data = request.execute()
				pdf_reader = PdfReader(io.BytesIO(base64.urlsafe_b64decode(file_data['data'])))
				page_one = pdf_reader.pages[0]
				text = page_one.extract_text()
				match = re.search(r'(\d{4,})', text)
				if match:
					file_id = match.group(1)
				else:
					file_id = 'NaN'

				# Construct filename
				filename = f'{file_id}|{date_str}.pdf'

				# Download attachment
				request = service.users().messages().attachments().get(
					userId='me', messageId=msg_id, id=attach_id).execute()
				file_data = base64.urlsafe_b64decode(request.get('data').encode('UTF-8'))
				with open(f'pdf_files/{filename}', 'wb') as thefile:
					thefile.write(file_data)

		service.users().messages().modify(userId='me', id=msg_id, body={
			'removeLabelIds': ['UNREAD']
		}).execute()

	print("Attachments downloaded Successfully!")
