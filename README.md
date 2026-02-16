# Visual Tokenizer

A Flask-based web application designed to provide detailed text analysis and metrics through tokenization and filtering.

## Description
This project allows users to input blocks of text and receive visual feedback on word counts, character counts, and frequency analysis. It features a flexible text-processing pipeline to handle tokenizatin, normalization, case sensitivity, and stop-word filtering.

## Technical Implementation
The application is built with a modular architecture:
- **Pipeline Pattern:** Orchestrates the text processing steps.
- **Service Layer:** Separates metrics calculation and text processing logic from the web routing.
- **Visualization:** Uses Chart.js for interactive frequency and Zipf's Law distribution charts.

## Getting Started

### Prerequisites
- Python 3.12+ (tested on 3.12)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd NLP-zipf-visualiser
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Access the web interface:**
   Open your browser and navigate to `http://127.0.0.1:5000`.


## Optional:
   Local txt files will appear as a dropdown option under data/corpora for backend processing if html request sizes become too large
## Acknowledgments
* NLTK for natural language processing.
* Chart.js for data visualization.
* MathJax for LaTeX rendering.

