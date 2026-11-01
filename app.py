from flask import Flask, render_template, request
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

application = Flask(__name__)
app = application


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/predictdata", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("home.html")

    categorical_fields = {
        "gender": {"female", "male"},
        "race_ethnicity": {"group A", "group B", "group C", "group D", "group E"},
        "parental_level_of_education": {
            "associate's degree",
            "bachelor's degree",
            "high school",
            "master's degree",
            "some college",
            "some high school",
        },
        "lunch": {"free/reduced", "standard"},
        "test_preparation_course": {"none", "completed"},
    }
    form_data = request.form
    for field, allowed_values in categorical_fields.items():
        if form_data.get(field) not in allowed_values:


            return render_template(
                "home.html", error=f"Please provide a valid {field.replace('_', ' ')}."
            ), 400

    try:
        reading_score = int(form_data.get("reading_score", ""))
        writing_score = int(form_data.get("writing_score", ""))
    except ValueError:
        return render_template(
            "home.html", error="Reading and writing scores must be whole numbers."
        ), 400

    if not (0 <= reading_score <= 100 and 0 <= writing_score <= 100):
        return render_template(
            "home.html", error="Reading and writing scores must be between 0 and 100."
        ), 400

    data = CustomData(
        gender=form_data["gender"],
        race_ethnicity=form_data["race_ethnicity"],
        parental_level_of_education=form_data["parental_level_of_education"],
        lunch=form_data["lunch"],
        test_preparation_course=form_data["test_preparation_course"],
        reading_score=reading_score,
        writing_score=writing_score,
    )
    prediction = PredictPipeline().predict(data.get_data_as_dataframe())
    return render_template("home.html", results=prediction[0])


if __name__ == "__main__":
    app.run()
