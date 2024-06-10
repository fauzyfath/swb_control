import tensorflow as tf
import numpy as np
from PIL import Image

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="Garbage_classification_model_lite.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define the class names
class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

def preprocess_image(image_path, input_shape):

    img = Image.open(image_path).resize((input_shape[1], input_shape[2]))
    img = np.array(img).astype('float32') / 255.0 
    img = np.expand_dims(img, axis=0) 
    return img

def predict_image(image_path):
    input_shape = input_details[0]['shape']
    input_data = preprocess_image(image_path, input_shape)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction_index = np.argmax(output_data)
    
    # Get the class name
    prediction_class = class_names[prediction_index]
    
    return prediction_class

# #output 
image_path = "C:\\Users\\fauzy\\Downloads\\20160728_192246_HDR.jpg" 
prediction = predict_image(image_path)
print(f"Prediction Object: {prediction}")
