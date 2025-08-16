from flask import Flask, request, render_template, flash, redirect, url_for,session, Response, render_template_string
from objective import ObjectiveTest
from subjective import SubjectiveTest
from readpdf import Extractpdf
import os 
import nltk


# Put NLTK data in a writable folder (persists across boots on Render)
NLTK_DATA_DIR = os.path.join(os.path.dirname(__file__), "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
if NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.insert(0, NLTK_DATA_DIR)

# Download only what we need; check both old and new resource names
NEEDED = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),  # new in recent NLTK
    ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),  # new name
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
]

for path, pkg in NEEDED:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg, download_dir=NLTK_DATA_DIR)

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# import nltk
# nltk.download("all")
# exit()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/input', methods=["POST"])
def input():
	return render_template('input.html')

@app.route('/upload', methods=["POST"])
def upload():
	return render_template('upload.html')

@app.route('/file_test_generate', methods=["POST"])
def file_test_generate():
	if request.method == "POST":
		inputFile = request.files["filename"]
		pgno = request.form["pgno"]
		testType = request.form["test_type"]
		noOfQues = request.form["noq"]
		readpdf_obj = Extractpdf(inputFile, pgno)
		inputText = readpdf_obj.read_content()
		if testType == "objective":
			objective_generator = ObjectiveTest(inputText,noOfQues)
			question_list, answer_list = objective_generator.generate_test()
			testgenerate = zip(question_list, answer_list)
			return render_template('generatedtestdata.html', cresults = testgenerate)
		elif testType == "subjective":
			subjective_generator = SubjectiveTest(inputText,noOfQues)
			question_list, answer_list = subjective_generator.generate_test()
			testgenerate = zip(question_list, answer_list)
			return render_template('generatedtestdata.html', cresults = testgenerate)
		else:
			flash('Error Ocuured!')
			return redirect(url_for('/'))

@app.route('/test_generate', methods=["POST"])
def test_generate():
	if request.method == "POST":
		inputText = request.form["itext"]
		testType = request.form["test_type"]
		noOfQues = request.form["noq"]
		if testType == "objective":
			objective_generator = ObjectiveTest(inputText,noOfQues)
			question_list, answer_list = objective_generator.generate_test()
			testgenerate = zip(question_list, answer_list)
			return render_template('generatedtestdata.html', cresults = testgenerate)
		elif testType == "subjective":
			subjective_generator = SubjectiveTest(inputText,noOfQues)
			question_list, answer_list = subjective_generator.generate_test()
			testgenerate = zip(question_list, answer_list)
			return render_template('generatedtestdata.html', cresults = testgenerate)
		else:
			flash('Error Ocuured!')
			return redirect(url_for('/'))

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port = 5001, debug=True)
