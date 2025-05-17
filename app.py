from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load the custom model
MODEL_PATH = "./model.hdf5"
model = load_model(MODEL_PATH, compile=False)

# Define the class labels
CLASS_LABELS = ['angry', 'disgust', 'sad', 'happy', 'neutral', 'scared', 'fear']

# Preprocessing function (update target_size as per your model's input)
def preprocess_image(img_path):
    img = image.load_img(img_path, color_mode='grayscale', target_size=(64, 64))
    img_array = image.img_to_array(img)  # shape: (64, 64, 1)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 64, 64, 1)
    return img_array

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Preprocess and predict
            img_array = preprocess_image(filepath)
            preds = model.predict(img_array)
            print("Prediction shape:", preds.shape)
            print("Prediction output:", preds)

            # Robust handling for different output shapes
            if preds is not None and preds.size > 0:
                if preds.ndim == 2 and preds.shape[0] == 1:
                    # Shape (1, 6)
                    pred_idx = np.argmax(preds[0])
                elif preds.ndim == 1 and preds.shape[0] == len(CLASS_LABELS):
                    # Shape (6,)
                    pred_idx = np.argmax(preds)
                else:
                    return jsonify({'error': f'Unexpected prediction shape: {preds.shape}'}), 500

                if pred_idx < len(CLASS_LABELS):
                    emotion = CLASS_LABELS[pred_idx]
                    print(f"Predicted emotion: {emotion}")
                else:
                    return jsonify({'error': f'Prediction index {pred_idx} out of range'}), 500
            else:
                return jsonify({'error': 'Model did not return a prediction'}), 500
            
            return jsonify({
                'success': True,
                'emotion': emotion,
                'image_url': f'/static/uploads/{filename}'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True) 