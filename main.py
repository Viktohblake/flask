from flask import Flask, redirect, render_template, request
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

app = Flask(__name__)

script_dir = os.path.dirname(__file__)
model_mobilenet_path = os.path.join(script_dir, 'MobileNetv2_leaf.h5')
model_resnet_path = os.path.join(script_dir, 'Resnet_leaf.h5')
model_inceptionv3_path = os.path.join(script_dir, 'Inceptionv3_leaf.h5')

model_mobilenet = load_model(model_mobilenet_path)
model_resnet = load_model(model_resnet_path)
model_inceptionv3 = load_model(model_inceptionv3_path)

if not os.path.exists(model_mobilenet_path):
    raise FileNotFoundError(f"Model file not found: {model_mobilenet_path}")
# Repeat for other models


def predict_image(image_path, model):
    img = image.load_img(image_path, target_size=(64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0 
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(np.array(prediction))
    return prediction, predicted_class_index

def predict_image75(image_path, model):
    img = image.load_img(image_path, target_size=(75, 75))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0 
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(np.array(prediction))
    return prediction, predicted_class_index

@app.route('/', methods=['GET', 'POST'])
def index():
    models = {
        'MobileNetV2': model_mobilenet,
        'ResNet50': model_resnet,
        'InceptionV3': model_inceptionv3
    }
    class_names = ['Health', 'Bacterial leaf blight', 'Brown spot', 'Leaf smut']
    predictions = {}

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join('static', 'images', file.filename)
            file.save(file_path)
            
            for model_name, model in models.items():
                if model_name != 'InceptionV3':
                    prediction, predicted_class_index = predict_image(file_path, model)
                    predicted_class = class_names[predicted_class_index]
                    predictions[model_name] = {'class': predicted_class, 'confidence': prediction[0][predicted_class_index]}
                else:
                    prediction, predicted_class_index = predict_image75(file_path, model)
                    predicted_class = class_names[predicted_class_index]
                    predictions[model_name] = {'class': predicted_class, 'confidence': prediction[0][predicted_class_index]}
            
            return render_template('index.html', predictions=predictions, image_path=file_path)
    return render_template('index.html', predictions=None, image_path=None)

if __name__ == '__main__':
    app.run()
