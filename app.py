from flask import Flask, render_template, request
import requests
from services.fetchers import fetch_gutenberg, fetch_wiki
from services.processor import run_pipeline
from services.steps import *
from services.metrics import (
    get_word_count, 
    get_unique_word_count, 
    get_character_count, 
    get_character_count_no_spaces
)
import os 

app = Flask(__name__)

@app.route('/')
def home ():
    techs = ['HTML', 'Flask', 'CSS', 'Python']
    name = 'NLP visualiser'
    return render_template('home.html', techs=techs, name=name, title='home')

@app.route('/about')
def about():
    name = 'NLP visualiser'
    return render_template('about.html', name = name, title = 'About Us')

@app.route('/post', methods = ['GET', 'POST'])
def post():
    name = 'NLP visualiser'
    if request.method == 'GET':
        # Default options for a clean state
        options = {
            'remove_punctuation': True,
            'filter_alpha': False,
            'case_sensitive': False,
            'remove_stop_words': False,
            'words_to_exclude': ''
        }
        return render_template('post.html', name = name, title = name, options=options, gutenberg_id='', wiki_query='')
    if request.method == 'POST':
        source = request.form.get('source-select')
        
        # Capture options early so they're available in error handlers
        options = {
            'remove_punctuation': request.form.get('remove_punctuation') == 'on',
            'filter_alpha': request.form.get('filter_alpha') == 'on',
            'case_sensitive': request.form.get('case_sensitive') == 'on',
            'remove_stop_words': request.form.get('remove_stop_words') == 'on',
            'words_to_exclude': request.form.get('words_to_exclude', '')
        }
        
        content = ""
        gutenberg_id = request.form.get('gutenberg_id', '')
        wiki_query = request.form.get('wiki_query', '')
        if source == 'Gutenberg':
            try:
                book_id = request.form.get('gutenberg_id')
                content = fetch_gutenberg(bookid=book_id)
            except requests.HTTPError as e:
                error_message = f"Book not found: {e.response.status_code} {e.response.reason}"
                return render_template('post.html', name=name, title=name, options=options, source=source, error=error_message, gutenberg_id=gutenberg_id)
            except requests.RequestException as e:
                error_message = "Network error. Please try again."
                return render_template('post.html', name=name, title=name, options=options, source=source, error=error_message,gutenberg_id=gutenberg_id) 
        elif source == 'Wikipedia':
            try:
                query = request.form.get('wiki_query')
                content = fetch_wiki(title=query)
            except ValueError as e:
                error_message = str(e)
                return render_template('post.html', name=name, title=name, options=options, source=source, error=error_message, wiki_query=wiki_query)
            except requests.RequestException as e:
                error_message = "Network error fetching Wikipedia article. Please try again."
                return render_template('post.html', name=name, title=name, options=options, source=source, error=error_message, wiki_query=wiki_query)
        else:
            content = request.form.get('content')

        # Build the pipeline based on toggles
        # Each step is now a tuple: (snapshot_name, function)
        steps = [('raw', tokenize_step)]
        
        if options['remove_punctuation']:
            steps.append(('cleaned_punct', remove_punctuation_step))

        if options['filter_alpha']:
            steps.append(('cleaned_alpha', filter_alpha_step))
        
        if not options['case_sensitive']:
            steps.append(('normalized', lowercase_step))
            
        # We'll take a snapshot here specifically for "before stop words" comparison
        # if the previous step wasn't already one of the others
        steps.append(('before_stop_words', lambda x: x)) 

        if options['remove_stop_words']:
            steps.append(('after_stop_words', remove_stop_words_step))

        if options['words_to_exclude']:
            words_to_exclude = options['words_to_exclude'].split(',')
            generated_function = create_exclusion_step(words_to_exclude)
            steps.append(('final', generated_function))
        else:
            # If no exclusion, the last step is 'final'
            steps.append(('final', lambda x: x))

        # Process the text
        processed_words, snapshots = run_pipeline(content, steps)
        
        # Get metrics
        word_count = get_word_count(processed_words)
        unique_word_count = get_unique_word_count(processed_words)
        char_count = get_character_count(content)
        char_count_no_spaces = get_character_count_no_spaces(content)
        
        # Prepare frequency data for comparison
        from services.metrics import get_most_frequent_words, get_zipf_data
        chart_data = {
            'before': get_most_frequent_words(snapshots.get('before_stop_words', []), n=50),
            'after': get_most_frequent_words(snapshots.get('final', []), n=50)
        }
        
        zipf_data = {
            'before': get_zipf_data(snapshots.get('before_stop_words', [])),
            'after': get_zipf_data(snapshots.get('final', []))
        }
        
        return render_template('post.html', 
                               name=name, 
                               title=name, 
                               content=content, 
                               source=source,
                               options=options,
                               word_count=word_count,
                               unique_word_count=unique_word_count,
                               char_count=char_count,
                               char_count_no_spaces=char_count_no_spaces,
                               chart_data=chart_data,
                               zipf_data=zipf_data)
        
        # return redirect(url_for('post'))

@app.route('/examples', methods = ['GET'])
def examples():
    name = 'NLP visualiser'
    corpora_dir = os.path.join(app.root_path, 'data', 'corpora')
    
    # 1. Get list of available files
    try:
        files = sorted([f for f in os.listdir(corpora_dir) if f.endswith('.txt')])
    except FileNotFoundError:
        files = []
    
    # 2. Get the selected file from query param
    selected_file = request.args.get('file', files[0] if files else None)
    
    # 3. Capture options from GET parameters or set defaults
    if not request.args:
        options = {
            'remove_punctuation': True,
            'filter_alpha': False,
            'case_sensitive': False,
            'remove_stop_words': False,
            'words_to_exclude': ''
        }
    else:
        options = {
            'remove_punctuation': request.args.get('remove_punctuation') == 'on',
            'filter_alpha': request.args.get('filter_alpha') == 'on',
            'case_sensitive': request.args.get('case_sensitive') == 'on',
            'remove_stop_words': request.args.get('remove_stop_words') == 'on',
            'words_to_exclude': request.args.get('words_to_exclude', '')
        }

    content = ""
    if selected_file:
        file_path = os.path.join(corpora_dir, selected_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {str(e)}"

    # 4. Build the pipeline based on options
    steps = [('raw', tokenize_step)]
    
    if options['remove_punctuation']:
        steps.append(('cleaned_punct', remove_punctuation_step))

    if options['filter_alpha']:
        steps.append(('cleaned_alpha', filter_alpha_step))
    
    if not options['case_sensitive']:
        steps.append(('normalized', lowercase_step))
        
    steps.append(('before_stop_words', lambda x: x)) 

    if options['remove_stop_words']:
        steps.append(('after_stop_words', remove_stop_words_step))

    if options['words_to_exclude']:
        words_to_exclude = options['words_to_exclude'].split(',')
        generated_function = create_exclusion_step(words_to_exclude)
        steps.append(('final', generated_function))
    else:
        steps.append(('final', lambda x: x))

    # Process the text
    processed_words, snapshots = run_pipeline(content, steps)
    
    # 5. Prepare metrics for visualization
    from services.metrics import get_most_frequent_words, get_zipf_data
    chart_data = {
        'before': get_most_frequent_words(snapshots.get('before_stop_words', []), n=50),
        'after': get_most_frequent_words(snapshots.get('final', []), n=50)
    }
    
    zipf_data = {
        'before': get_zipf_data(snapshots.get('before_stop_words', [])),
        'after': get_zipf_data(snapshots.get('final', []))
    }
    
    return render_template('examples.html', 
                           name=name, 
                           title="Corpora Examples", 
                           files=files, 
                           selected_file=selected_file,
                           options=options,
                           chart_data=chart_data,
                           zipf_data=zipf_data)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)
