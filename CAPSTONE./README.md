# RetinaAI — Diabetic Retinopathy Screening (Academic Prototype)

RetinaAI is a college-level Flask web application that demonstrates five-class diabetic-retinopathy image classification from retinal fundus photographs. It uses a pretrained EfficientNetB0 model and presents the model output in a browser interface.

> **Research/academic demonstration only. Not a medical device or diagnostic system.** Predictions may be incorrect. Do not use this application to make health decisions; consult a qualified eye-care professional.

## Features

- Upload and preview retinal fundus images (JPG/JPEG/PNG; maximum 12 MB).
- Validate uploaded image files and convert valid images to RGB.
- Resize input images to 224 × 224 before inference.
- Run a pretrained five-class EfficientNetB0 model.
- Display predicted grade, model score and five class scores.
- Show basic technical image metrics (dimensions, average brightness and grayscale contrast).
- Show educational information for the predicted category.
- Display the top-two score gap as an uncertainty prompt (not calibrated clinical certainty).
- Keep temporary screening history in the current browser session.
- Print the result and download a JSON report.

## Five output classes

| Grade | Label |
|---:|---|
| 0 | No DR |
| 1 | Mild |
| 2 | Moderate |
| 3 | Severe |
| 4 | Proliferative DR |

## Technology stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Image handling:** Pillow, NumPy
- **Deep learning:** Keras with TensorFlow backend
- **Model download:** Hugging Face Hub

## Repository structure

```text
retinaai_project/
├── app.py                     # Flask routes, model loading and prediction logic
├── train.py                   # Optional APTOS-style training starter script
├── requirements.txt           # Runtime dependencies
├── requirements-training.txt  # Runtime dependencies plus pandas for train.py
├── setup_windows.bat          # Installs dependencies on Windows
├── start_windows.bat          # Starts the local Flask website
├── templates/
│   └── index.html             # Main website page
├── static/
│   ├── app.js                 # Upload, API call, results, history and report UI
│   └── style.css              # Website styling
├── PROJECT_MODULES.md         # Suggested three-module/student contribution split
├── REFERENCES.md              # Third-party model, dataset and framework links
└── README.md
```

Runtime-created folders such as `uploads/`, local model files and Python cache files are excluded from Git using `.gitignore`.

## Run on Windows

### Requirements

- Windows 10/11, 64-bit
- Python 3.11 (recommended; use a compatible 64-bit Python 3.10–3.12 environment)
- Internet connection for the first model download

### Start

1. Download or clone this repository.
2. Open the project folder containing `app.py`.
3. Double-click `setup_windows.bat` and wait for installation to finish.
4. Double-click `start_windows.bat`.
5. On first launch, the application downloads `final_model.keras` from Hugging Face. Keep the internet connection active and wait for `Retinal grading model loaded successfully.`
6. Open <http://127.0.0.1:5000> in your browser.
7. Keep the terminal window open while using the website. Press `Ctrl+C` in that window to stop the server.

The model file is cached by Hugging Face in the user's local cache; it is not committed to this repository. Subsequent launches normally use the cached file.

### PowerShell alternative

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

If `python` is not on PATH, replace `python` with the full path to your Python 3.11 executable.

## API endpoints

### `GET /api/status`

Returns whether the model loaded, its repository ID, and a model-loading error if present.

### `POST /api/analyze`

Accepts multipart form data with an `image` file. On success, returns JSON containing the predicted grade, label, model score, class probabilities, image-quality metrics and educational context. Invalid files or inference failures return an error response.

## How the application works

1. The user selects a retinal fundus photograph.
2. Flask validates the extension and verifies that the file is a readable image.
3. The image is converted to RGB and resized to 224 × 224 pixels.
4. The pretrained EfficientNetB0 model produces five class scores.
5. The highest-scoring class is displayed with the scores and supporting interface information.
6. The temporary uploaded file is deleted after processing.

## Model and dataset notes

- **Model repository:** [Aldahmashi/DR-EfficientNetB0](https://huggingface.co/Aldahmashi/DR-EfficientNetB0)
- **Dataset referenced by the model:** [APTOS 2019 Blindness Detection](https://www.kaggle.com/competitions/aptos2019-blindness-detection)
- The model card reports its own evaluation metrics. Those metrics are not results independently measured by this student project. Refer to the model card for its current reported results and limitations.
- The model is pretrained by a third party; this repository integrates it for inference. Do not claim the team trained this exact model from scratch.
- Review the model and dataset licenses/terms before redistribution. See [REFERENCES.md](REFERENCES.md).

## Optional training starter

`train.py` is an optional starter script for an APTOS-style CSV with `id_code` and `diagnosis` columns and image files named `<id_code>.png` in a directory. Install its extra dependency with:

```powershell
python -m pip install -r requirements-training.txt
```

Example:

```powershell
python train.py --csv train.csv --images ./train_images --epochs 8
```

This script is a basic starting point, not a complete validated training/evaluation pipeline. Before reporting any accuracy, create separate training, validation and test splits (preferably patient-level where identifiers permit), address class imbalance, evaluate per-class precision/recall/F1 and confusion matrix, and document preprocessing consistency. The website currently loads the published Hugging Face model, not the `model/retina_model.keras` output of this starter script.

## Suggested three-student module division

See [PROJECT_MODULES.md](PROJECT_MODULES.md). Update the student names and responsibilities to reflect the work actually completed by each team member.

## Limitations and responsible use

- This is an academic prototype, not a clinically validated diagnostic system.
- The pretrained model was developed using a specific dataset; performance on images from other cameras, settings or populations is not established here.
- A predicted class and its score can be wrong. The score is not a calibrated probability of disease or clinical certainty.
- Image brightness/contrast/dimension checks are simple technical heuristics. They do not detect lesions or certify clinical image quality.
- Educational grade descriptions are general information, not lesion explanations generated from the uploaded image.
- No uploaded images are intended to be retained by the server; temporary files are removed after processing. Browser history is session-only.
