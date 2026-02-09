from flask import Flask, render_template, request
import requests
from services.fetchers import fetch_gutenberg, fetch_wiki
from services.processor import run_pipeline
from services.steps import *
from services.metrics import (
    get_word_count, 
    get_unique_word_count, 
    get_character_count, 
    get_character_count_no_spaces,
    get_most_frequent_words,
    get_zipf_data
)
import os 

app = Flask(__name__)

APP_NAME = 'NLP visualiser'

DEFAULT_OPTIONS = {
    'remove_punctuation': True,
    'filter_alpha': False,
    'case_sensitive': False,
    'remove_stop_words': False,
    'words_to_exclude': ''
}


def parse_options(data):
    """Parse analysis options from a request form or query args."""
    return {
        'remove_punctuation': data.get('remove_punctuation') == 'on',
        'filter_alpha': data.get('filter_alpha') == 'on',
        'case_sensitive': data.get('case_sensitive') == 'on',
        'remove_stop_words': data.get('remove_stop_words') == 'on',
        'words_to_exclude': data.get('words_to_exclude', '')
    }


def build_pipeline(options):
    """Build a processing pipeline from the given options."""
    steps = [('raw', tokenize_step)]

    if options['remove_punctuation']:
        steps.append(('cleaned_punct', remove_punctuation_step))

    if options['filter_alpha']:
        steps.append(('cleaned_alpha', filter_alpha_step))

    if not options['case_sensitive']:
        steps.append(('normalized', lowercase_step))

    # Snapshot before stop-word removal for comparison charts
    steps.append(('before_stop_words', lambda x: x))

    if options['remove_stop_words']:
        steps.append(('after_stop_words', remove_stop_words_step))

    if options['words_to_exclude']:
        words = options['words_to_exclude'].split(',')
        steps.append(('final', create_exclusion_step(words)))
    else:
        steps.append(('final', lambda x: x))

    return steps


def analyze(content, options):
    """Run the pipeline and return all metrics and chart data."""
    steps = build_pipeline(options)
    processed_words, snapshots = run_pipeline(content, steps)

    return {
        'word_count': get_word_count(processed_words),
        'unique_word_count': get_unique_word_count(processed_words),
        'char_count': get_character_count(content),
        'char_count_no_spaces': get_character_count_no_spaces(content),
        'chart_data': {
            'before': get_most_frequent_words(snapshots.get('before_stop_words', []), n=50),
            'after': get_most_frequent_words(snapshots.get('final', []), n=50),
        },
        'zipf_data': {
            'before': get_zipf_data(snapshots.get('before_stop_words', [])),
            'after': get_zipf_data(snapshots.get('final', [])),
        },
    }


def fetch_content(source, form):
    """Fetch text content based on the selected source.

    Returns (content, error_message).  error_message is None on success.
    """
    if source == 'Gutenberg':
        try:
            return fetch_gutenberg(bookid=form.get('gutenberg_id')), None
        except requests.HTTPError as e:
            return None, f"Book not found: {e.response.status_code} {e.response.reason}"
        except requests.RequestException:
            return None, "Network error. Please try again."

    if source == 'Wikipedia':
        try:
            return fetch_wiki(title=form.get('wiki_query')), None
        except ValueError as e:
            return None, str(e)
        except requests.RequestException:
            return None, "Network error fetching Wikipedia article. Please try again."

    # Default: pasted text
    return form.get('content', ''), None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('home.html',
                           techs=['HTML', 'Flask', 'CSS', 'Python'],
                           name=APP_NAME, title='home')


@app.route('/about')
def about():
    return render_template('about.html', name=APP_NAME, title='About Us')


@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        return render_template('post.html',
                               name=APP_NAME, title=APP_NAME,
                               options=DEFAULT_OPTIONS,
                               gutenberg_id='', wiki_query='')

    # -- POST -----------------------------------------------------------------
    source = request.form.get('source-select')
    options = parse_options(request.form)
    gutenberg_id = request.form.get('gutenberg_id', '')
    wiki_query = request.form.get('wiki_query', '')

    # Shared template context for every render in this route
    ctx = dict(name=APP_NAME, title=APP_NAME, source=source,
               options=options, gutenberg_id=gutenberg_id,
               wiki_query=wiki_query)

    content, error = fetch_content(source, request.form)
    if error:
        return render_template('post.html', **ctx, error=error)

    results = analyze(content, options)

    # Only send pasted text back to the textarea; Gutenberg/Wikipedia
    # content is re-fetchable from the ID/title and would otherwise
    # trigger a 413 (Request Entity Too Large) on the next submission.
    return render_template('post.html', **ctx, **results,
                           content=content if source == 'Paste' else '')


@app.route('/examples', methods=['GET'])
def examples():
    corpora_dir = os.path.join(app.root_path, 'data', 'corpora')

    try:
        files = sorted(f for f in os.listdir(corpora_dir) if f.endswith('.txt'))
    except FileNotFoundError:
        files = []

    selected_file = request.args.get('file', files[0] if files else None)
    options = parse_options(request.args) if request.args else DEFAULT_OPTIONS.copy()

    content = ""
    if selected_file:
        try:
            with open(os.path.join(corpora_dir, selected_file),
                      'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {str(e)}"

    results = analyze(content, options)

    return render_template('examples.html',
                           name=APP_NAME, title="Corpora Examples",
                           files=files, selected_file=selected_file,
                           options=options, **results)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)
