"""
Transfer-learning training script for an APTOS-style CSV dataset.
Expected CSV columns: id_code, diagnosis. Image files: <id_code>.png in --images.
Install TensorFlow separately as described in README before running.
"""
import argparse
from pathlib import Path
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers

parser=argparse.ArgumentParser()
parser.add_argument("--csv",required=True,help="Training labels CSV")
parser.add_argument("--images",required=True,help="Directory containing retinal images")
parser.add_argument("--epochs",type=int,default=8)
args=parser.parse_args()

df=pd.read_csv(args.csv)
required={"id_code","diagnosis"}
if not required.issubset(df.columns): raise ValueError("CSV must contain id_code and diagnosis columns")
paths=[str(Path(args.images)/(str(x)+".png")) for x in df.id_code]
labels=df.diagnosis.astype(int).tolist()
missing=[p for p in paths if not Path(p).exists()]
if missing: raise FileNotFoundError(f"{len(missing)} images missing. First: {missing[0]}")

ds=tf.data.Dataset.from_tensor_slices((paths,labels))
def load(path,label):
    image=tf.io.read_file(path)
    image=tf.image.decode_image(image,channels=3,expand_animations=False)
    image=tf.image.resize(image,(224,224))/255.0
    return image,tf.one_hot(label,5)
ds=ds.map(load,num_parallel_calls=tf.data.AUTOTUNE).shuffle(len(df)).batch(16).prefetch(tf.data.AUTOTUNE)
base=tf.keras.applications.EfficientNetB0(include_top=False,weights="imagenet",input_shape=(224,224,3))
base.trainable=False
inputs=layers.Input((224,224,3))
x=base(inputs,training=False)
x=layers.GlobalAveragePooling2D()(x)
x=layers.Dropout(.3)(x)
outputs=layers.Dense(5,activation="softmax")(x)
model=tf.keras.Model(inputs,outputs)
model.compile(optimizer="adam",loss="categorical_crossentropy",metrics=["accuracy"])
model.fit(ds,epochs=args.epochs)
out=Path("model");out.mkdir(exist_ok=True)
model.save(out/"retina_model.keras")
print("Saved model/retina_model.keras. Evaluate on a separate patient-level test set before reporting performance.")
