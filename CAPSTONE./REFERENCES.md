# References and Third-Party Resources

The project uses a third-party pretrained model and refers to the APTOS 2019 dataset. Review the current license and usage conditions on each source page before redistributing the model, dataset, or derived materials.

- **Pretrained model:** [Aldahmashi/DR-EfficientNetB0 on Hugging Face](https://huggingface.co/Aldahmashi/DR-EfficientNetB0)
- **Dataset:** [APTOS 2019 Blindness Detection on Kaggle](https://www.kaggle.com/competitions/aptos2019-blindness-detection)
- **Frameworks:** [Flask](https://flask.palletsprojects.com/), [Keras](https://keras.io/), [TensorFlow](https://www.tensorflow.org/), [Hugging Face Hub](https://huggingface.co/docs/huggingface_hub/)

The website downloads `final_model.keras` from the model repository on first launch using `huggingface_hub`. The model weights are not stored in this GitHub source repository.
