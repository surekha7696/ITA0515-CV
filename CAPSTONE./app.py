from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import os, uuid

# Keras 3 uses TensorFlow as its backend for this project.
os.environ.setdefault("KERAS_BACKEND", "tensorflow")

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED = {"png", "jpg", "jpeg"}
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

LABELS = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
MODEL_ID = "Aldahmashi/DR-EfficientNetB0"
MODEL = None
MODEL_ERROR = None


def load_model():
    """Load the published five-class APTOS EfficientNetB0 model from Hugging Face.

    The first run downloads final_model.keras (~33.4 MB) into the Hugging Face
    cache. Later runs load the cached file. The model is loaded as a local .keras
    archive because this repository does not expose a root config.json.
    """
    global MODEL_ERROR
    try:
        import keras
        from huggingface_hub import hf_hub_download
        print(f"Downloading retinal grading model: {MODEL_ID}")
        # This repository stores the model as final_model.keras. Download that
        # archive explicitly, then load it as a local Keras file. Loading the
        # repository root through hf:// expects a config.json that this repo
        # does not provide, which caused the user's missing-config error.
        model_file = hf_hub_download(
            repo_id=MODEL_ID,
            filename="final_model.keras",
        )
        print(f"Loading model file: {model_file}")
        model = keras.saving.load_model(model_file)
        print("Retinal grading model loaded successfully.")
        return model
    except Exception as exc:
        MODEL_ERROR = str(exc)
        print("MODEL LOAD ERROR:", MODEL_ERROR)
        return None


MODEL = load_model()


def assess_image_quality(path):
    """Simple technical image checks; these are not clinical quality judgments."""
    import numpy as np
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        width, height = rgb.size
        gray = np.asarray(rgb.convert("L"), dtype="float32")
    brightness = float(gray.mean())
    contrast = float(gray.std())
    notes = []
    if min(width, height) < 224:
        notes.append("Image resolution is below the model input size; fine details may be limited.")
    if brightness < 35:
        notes.append("Image appears very dark; use a better illuminated fundus photograph if available.")
    elif brightness > 220:
        notes.append("Image appears very bright; glare or overexposure may affect image details.")
    if contrast < 20:
        notes.append("Image contrast is low; retinal structures may be difficult to distinguish.")
    if not notes:
        notes.append("Basic resolution, brightness and contrast checks passed. This does not confirm clinical image quality.")
    status = "Review recommended" if len(notes) > 1 or min(width, height) < 224 else "Basic checks passed"
    return {
        "width": width, "height": height,
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "status": status,
        "notes": notes,
    }


def grade_information(grade):
    """Educational context for model output; not a diagnosis or image finding."""
    info = [
        ("No DR", "The model assigned the image to its no-apparent-DR training class.", "A model result cannot rule out eye disease. Continue routine eye examinations as advised by an eye-care professional."),
        ("Mild DR", "The mild class is associated in clinical grading systems with early changes such as microaneurysms.", "Arrange review with a qualified eye-care professional; follow their recommended diabetic eye-screening schedule."),
        ("Moderate DR", "The moderate class represents more retinal changes than the mild class in the grading scheme.", "Seek assessment by an eye-care professional to confirm the finding and determine appropriate follow-up."),
        ("Severe DR", "The severe class represents advanced non-proliferative changes in the grading scheme.", "Prompt professional eye assessment is important. Do not rely on this prototype to decide treatment."),
        ("Proliferative DR", "The proliferative class is the most advanced category in this five-grade scheme.", "Prompt assessment by an ophthalmologist is important. This website cannot confirm or exclude this condition."),
    ]
    return {"title": info[grade][0], "about": info[grade][1], "next_step": info[grade][2]}


def predict_image(path):
    if MODEL is None:
        raise RuntimeError(
            "The AI model could not be loaded. Check your internet connection on "
            "the first run and install requirements using setup_windows.bat. "
            f"Details: {MODEL_ERROR or 'unknown model loading error'}"
        )

    import numpy as np
    # Model card example: RGB, 224x224, float32 pixel values (0..255).
    quality = assess_image_quality(path)
    image = Image.open(path).convert("RGB").resize((224, 224))
    arr = np.asarray(image, dtype="float32")
    probs = np.asarray(MODEL.predict(arr[None, ...], verbose=0)[0], dtype="float64")
    if probs.shape[0] != 5:
        raise RuntimeError(f"Expected 5 model outputs, received {probs.shape[0]}.")
    probs = np.clip(probs, 0, None)
    total = float(probs.sum())
    if total <= 0:
        raise RuntimeError("The model returned invalid probability values.")
    probs = probs / total
    idx = int(np.argmax(probs))
    ordered = np.sort(probs)
    confidence_gap = round(float((ordered[-1] - ordered[-2]) * 100), 1)
    confidence = round(float(probs[idx]) * 100, 1)
    caution = ("The two highest class scores are close; treat this prediction cautiously." if confidence_gap < 10
               else "Model confidence is a score, not a measure of clinical certainty.")
    return {
        "mode": "trained_model",
        "grade": idx,
        "label": LABELS[idx],
        "confidence": confidence,
        "confidence_gap": confidence_gap,
        "caution": caution,
        "grade_information": grade_information(idx),
        "image_quality": quality,
        "probabilities": [round(float(x) * 100, 1) for x in probs],
        "message": (
            "Prediction generated by a pretrained EfficientNetB0 model based on "
            "APTOS 2019. Academic demonstration only; not a medical diagnosis."
        ),
    }


@app.route("/")
def home():
    return render_template("index.html", model_ready=MODEL is not None)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify(error="Please choose a retinal image."), 400
    file = request.files["image"]
    if not file.filename:
        return jsonify(error="Please choose a file first."), 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        return jsonify(error="Supported formats: JPG, JPEG and PNG."), 400

    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    path = UPLOAD_DIR / filename
    try:
        file.save(path)
        with Image.open(path) as im:
            im.verify()
        result = predict_image(path)
        result["filename"] = secure_filename(file.filename)
        return jsonify(result)
    except UnidentifiedImageError:
        return jsonify(error="The file is not a readable image. Upload a valid JPG or PNG retinal photograph."), 400
    except RuntimeError as exc:
        return jsonify(error=str(exc), model_ready=MODEL is not None), 503
    except Exception as exc:
        app.logger.exception("Image analysis failed")
        return jsonify(error=f"Image analysis failed: {exc}"), 500
    finally:
        path.unlink(missing_ok=True)


@app.route("/api/status")
def status():
    return jsonify(model_ready=MODEL is not None, model_id=MODEL_ID,
                   model_error=MODEL_ERROR if MODEL is None else None)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
