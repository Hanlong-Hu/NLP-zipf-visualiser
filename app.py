from flask import Flask, render_template, request, redirect, url_for
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
    name = 'Text Analyzer'
    return render_template('home.html', techs=techs, name=name, title='home')

@app.route('/about')
def about():
    name = 'Text Analyzer'
    return render_template('about.html', name = name, title = 'About Us')

@app.route('/post', methods = ['GET', 'POST'])
def post():
    name = 'Text Analyzer'
    if request.method == 'GET':
        # Default options for a clean state
        options = {
            'remove_punctuation': True,
            'filter_alpha': False,
            'case_sensitive': False,
            'remove_stop_words': False,
            'words_to_exclude': ''
        }
        return render_template('post.html', name = name, title = name, options=options)
    if request.method == 'POST':
        content = request.form['content']
        
        # Capture options for maintaining state
        options = {
            'remove_punctuation': request.form.get('remove_punctuation') == 'on',
            'filter_alpha': request.form.get('filter_alpha') == 'on',
            'case_sensitive': request.form.get('case_sensitive') == 'on',
            'remove_stop_words': request.form.get('remove_stop_words') == 'on',
            'words_to_exclude': request.form.get('words_to_exclude', '')
        }

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
        
        # Prepare frequency data for comparison (Top 50 for performance and readability)
        from services.metrics import get_most_frequent_words
        chart_data = {
            'before': get_most_frequent_words(snapshots.get('before_stop_words', []), n=50),
            'after': get_most_frequent_words(snapshots.get('final', []), n=50)
        }
        
        
        return render_template('post.html', 
                               name=name, 
                               title=name, 
                               content=content, 
                               options=options,
                               word_count=word_count,
                               unique_word_count=unique_word_count,
                               char_count=char_count,
                               char_count_no_spaces=char_count_no_spaces,
                               chart_data=chart_data)
        
        # return redirect(url_for('post'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
