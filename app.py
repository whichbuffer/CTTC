from flask import Flask, render_template, redirect, url_for, flash,jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
import requests
import openai
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now retrieve the API key
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Missing OpenAI API key")

# You can now use the openai_api_key in your application



app = Flask(__name__)
# A secret key is needed to use Flask sessions and CSRF protection in Flask-WTF
app.config['SECRET_KEY'] = 'your_secret_key'

# Headers for making HTTP requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

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

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ThreatResearchForm()
    course_of_action = None

    if form.validate_on_submit():
        data = ""
        try:
            response = requests.get(form.url.data, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            unwanted_divs = soup.find_all('div', class_='tab-content')
            for unwanted_div in unwanted_divs:
                unwanted_div.decompose()

            unwanted_classes = ['cz-related-article-wrapp', 'bc_downloads','bc_copyright','cz-comment-loggin-wrapp']
            for class_name in unwanted_classes:
                for unwanted_div in soup.find_all('div', class_=class_name):
                    unwanted_div.decompose()

            data = " ".join([p.get_text() for p in soup.find_all('p')])

        except:
            flash('Failed to fetch URL content.', 'error')
            return redirect(url_for('index'))

        MAX_TOKENS = 4000
        if len(data) > MAX_TOKENS:
            data = data[:MAX_TOKENS]

        message_content = f"URL content:\n{data}\n"
        if form.summarize_event.data:
            message_content += "Please summarize this event.\n"
        for action in form.actions.data:
            message_content += f"Give me a {action} method against the above content.\n"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message_content}
            ]
        )
        course_of_action = format_course_of_action(response.choices[0].message['content'])

    return render_template('index.html', form=form, course_of_action=course_of_action)



if __name__ == '__main__':
    app.run(debug=True)
