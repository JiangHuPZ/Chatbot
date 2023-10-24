from flask import Flask, request, jsonify
from quary import qa_with_sources

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get("question")

        result = qa_with_sources({"query": question})
        response = result["result"]

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
