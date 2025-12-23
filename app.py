from flask import Flask, render_template, request, redirect, url_for
from services.count import count_words
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
        return render_template('post.html', name = name, title = name)
    if request.method == 'POST':
        content = request.form['content']
        print(content)
        word_count = count_words(content)
        return render_template('post.html', name = name, title = name, content = content, word_count = word_count)
        
        # return redirect(url_for('post'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
