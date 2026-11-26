# Project Modules and Student Contributions

Use this as a suggested division for a three-student team. Update student names and tasks to match the work each person actually completed.

## Module 1 — Retinal Image Dataset and Preprocessing

**Suggested owner:** Student 1

- Identify and organise retinal fundus images and their five severity labels.
- Validate image file formats and inspect image dimensions.
- Convert images to RGB and resize to the model input size (224 × 224).
- Prepare the labelled dataset for model development and testing.

**Output:** Organised retinal image dataset and preprocessing workflow.

## Module 2 — AI-Based Diabetic Retinopathy Classification

**Suggested owner:** Student 2

- Integrate the pretrained EfficientNetB0 model published as `Aldahmashi/DR-EfficientNetB0`.
- Prepare the image tensor and run model inference.
- Map the five output scores to No DR, Mild, Moderate, Severe and Proliferative DR.
- Return the predicted grade, model score and class probabilities.

**Output:** Five-class image classification inference component.

## Module 3 — Flask Website and Result Presentation

**Suggested owner:** Student 3

- Build the browser interface using HTML, CSS and JavaScript.
- Implement image upload, preview and client-side interaction.
- Connect the interface to the Flask `/api/analyze` endpoint.
- Display the prediction, class scores, technical image checks and educational context.
- Provide session history, print view and JSON report download.

**Output:** Web application integrating the image classifier.

## End-to-end flow

Retinal image upload → file validation → RGB conversion and resize → EfficientNetB0 inference → five class scores → result display and report.

> This is a suggested responsibility split. Only list tasks as an individual contribution if that student actually performed or contributed to them.
