# Standard libraries
import os
import re
import logging

# Third-party libraries
from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Constants
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
UNWANTED_CLASSES = ['cz-related-article-wrapp', 'bc_downloads', 'bc_copyright', 'cz-comment-loggin-wrapp','copy','bc_right_sidebar','srpw_widget-3','entry-author','textwidget','marketo-blog-subscribe']
MAX_TOKENS = 4000

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
def load_environment_vars():
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("Missing OpenAI API key")
    secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Fallback to 'default_secret_key' if not specified
    return openai_api_key, secret_key

OPENAI_API_KEY, SECRET_KEY = load_environment_vars()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY




# Form Definitions
class ThreatResearchForm(FlaskForm):
    url = StringField('URL of the threat research', validators=[DataRequired()])
    actions = SelectMultipleField('Choose Course of Action', choices=[
        ('prevention', 'Prevention'),
        ('detection', 'Detection')
    ], widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    summarize_event = BooleanField('Summarize Event')
    submit = SubmitField('Submit')

def format_course_of_action(coa_text):
    lines = coa_text.split('\n')
    formatted_text = []
    is_list = False
    current_item = ""

    for line in lines:
        line = line.strip()
        if re.match(r"^\d+", line):
            is_list = True
            if current_item:
                formatted_text.append(f"<li>{current_item}</li>")
                current_item = ""
            current_item = re.sub(r"^\d+[.\s]*", "", line).strip()
        else:
            if is_list:
                current_item += " " + line
            else:
                formatted_text.append(f"<p>{line}</p>")

    if current_item:
        formatted_text.append(f"<li>{current_item}</li>")

    if is_list:
        return f"<ul>{''.join(formatted_text)}</ul>"
    else:
        return ''.join(formatted_text)

def split_text_into_chunks(text, max_size):
    """
    Splits the given text into chunks that are approximately max_size long.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    current_length = 0
    for word in words:
        if current_length + len(word) <= max_size:
            current_chunk.append(word)
            current_length += len(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)

    chunks.append(' '.join(current_chunk))
    return chunks

def extract_data_from_url(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for class_name in UNWANTED_CLASSES:
            for unwanted_element in soup.find_all(class_=class_name):
                unwanted_element.decompose()

        extracted_text = " ".join([p.get_text() for p in soup.find_all('p')])
        
        # Remove Unicode escape sequences using regex
        cleaned_text = re.sub(r'\\\\u[0-9a-fA-F]{4}', '', extracted_text)
        cleaned_text = cleaned_text.replace('\u00a0', ' ')
  



        return cleaned_text

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL content. Error: {e}")

    
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ThreatResearchForm()
    course_of_action = ""

    if form.validate_on_submit():
        try:
            data = extract_data_from_url(form.url.data)
            data_chunks = split_text_into_chunks(data, MAX_TOKENS)
            
            # Combine all chunks into a single message
            all_data = "\n\n".join(data_chunks)
            messages = [{"role": "user", "content": f"URL content:\n{all_data}\n"}]

            if form.summarize_event.data:
                messages.append({"role": "user", "content": "Please summarize this event."})
                
            for action in form.actions.data:
                action_message = f"Give me actionable {action} logic against it. I want you to give mentions such as I saw xyz in the article that you provided and here is the {action}."
                messages.append({"role": "user", "content": action_message})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            course_of_action += format_course_of_action(response.choices[0].message['content'])

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('index'))

    return render_template('index.html', form=form, course_of_action=course_of_action)





if __name__ == '__main__':
    app.run(debug=True)
