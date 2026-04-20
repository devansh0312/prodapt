from flask import Flask, render_template, request

from main import handle_query


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    query = ""
    mode = "strict"

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        mode = request.form.get("mode", "strict").strip().lower()

        if not query:
            error = "Please enter a customer complaint before generating a response."
        else:
            try:
                result = handle_query(query, mode)
            except Exception as exc:
                error = f"Something went wrong while generating the response: {exc}"

    return render_template(
        "index.html",
        result=result,
        error=error,
        query=query,
        mode=mode,
    )


if __name__ == "__main__":
    app.run(debug=True)
