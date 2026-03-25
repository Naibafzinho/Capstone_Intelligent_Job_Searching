from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/recommendations')
def get_recommendations():
    # Later replace this with your NLP output
    skills = ["Python", "Machine Learning", "SQL", "Decision Making"]
    return jsonify(skills)

if __name__ == '__main__':
    app.run(debug=True)