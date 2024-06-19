from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import os
import pandas as pd
import re
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

AIKitchen = Flask(__name__)
AIKitchen.secret_key = 'Tech_Pioneers'

class_names = ["asafoetida", "brown rice", "butter", "cabbage", "capsicum", "cardamom powder", "carom seeds",
               "carrot", "coriander leaves", "curry leaves", "dry red chili", "eggplant", "fenugreek leaves",
               "fenugreek seeds", "garlic", "ginger", "green chili", "jaggery", "lemon", "mango", "milk",
               "mustard seeds", "onion", "raw mango", "red chili powder", "ridge gourd skin", "rosemary",
               "saffron strands", "sugar", "sunflower oil", "tamarind", "tea leaves", "tomato", "turmeric powder",
               "white lentils", "yellow corn meal flour"]

UPLOAD_FOLDER = '/Intel Project/Intel_Customized_AI_Kitchen/static/uploaded_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
AIKitchen.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
AIKitchen.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AIKitchen.config['ALLOWED_EXTENSIONS']


def parse_amount(amount):
    match = re.match(r'(\d+/\d+|\d+\.\d+|\d+)(.*)', amount.strip())
    if match:
        quantity = match.group(1)
        unit = match.group(2).strip()
        return quantity, unit
    return None, amount


def check_ingredients(predictions_list, ingredient_names):
    available_ingredients = [ingredient for ingredient in ingredient_names if ingredient in predictions_list]
    return available_ingredients, len(available_ingredients) == len(ingredient_names)


file_path = '/Intel Project/Intel_Customized_AI_Kitchen/Custom_Recipe_Dataset.csv'

try:
    df = pd.read_csv(file_path, encoding='latin1')
except FileNotFoundError:
    raise Exception(f"The file at path {file_path} was not found. Please check the path and try again.")


@AIKitchen.route('/')
def index():
    dishes = df['RecipeName'].tolist()
    return render_template('index.html', dishes=dishes)


@AIKitchen.route('/select_dish', methods=['POST'])
def select_dish():
    selected_dish_index = int(request.form['dish']) - 1
    num_people = int(request.form['num_people'])
    session['selected_dish_index'] = selected_dish_index
    session['num_people'] = num_people
    return redirect(url_for('action'))


@AIKitchen.route('/action', methods=['GET', 'POST'])
def action():
    if request.method == 'POST':
        action_type = request.form.get('action')
        if action_type == 'upload':
            return redirect(url_for('upload_files'))
        elif action_type == 'keep':
            return redirect(url_for('classify_images'))
        else:
            return jsonify({'message': 'Invalid action.'}), 400
    return render_template('action.html')


@AIKitchen.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({'message': 'No files part in the request'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'message': 'No files uploaded'}), 400

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(AIKitchen.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

        return redirect(url_for('classify_images'))
    return render_template('upload.html')


@AIKitchen.route('/classify')
def classify_images():
    selected_dish_index = session.get('selected_dish_index')
    num_people = session.get('num_people')

    if selected_dish_index is None or num_people is None:
        return redirect(url_for('index'))

    selected_dish = df.iloc[selected_dish_index]
    servings = selected_dish['Servings']
    ingredients = selected_dish['Ingredients']
    amounts = selected_dish['Amount']
    ingredients_list = ingredients.split(',')
    amounts_list = amounts.split(',')

    multiplied_ingredients = []
    for ingredient, amount in zip(ingredients_list, amounts_list):
        quantity, unit = parse_amount(amount)
        if quantity is not None:
            try:
                quantity_float = float(quantity)
            except ValueError:
                quantity_float = None

            if quantity_float is not None:
                quantity_float *= num_people / servings
                multiplied_ingredients.append((ingredient.strip(), f"{quantity_float} {unit}".strip()))
            else:
                multiplied_ingredients.append((ingredient.strip(), f"{quantity} {unit}".strip()))
        else:
            multiplied_ingredients.append((ingredient.strip(), f"{amount.strip()} (quantity not specified)"))

    ingredients_df = pd.DataFrame(multiplied_ingredients, columns=['Ingredient', 'Amount'])
    ingredient_names = [ingredient[0] for ingredient in multiplied_ingredients]

    cnn = tf.keras.models.load_model(
        '/Intel Project/Intel_Customized_AI_Kitchen/Custom_Image_Classification_Trained_Model.h5')

    input_folder = AIKitchen.config['UPLOAD_FOLDER']
    predictions_list = []
    image_filenames = sorted([f for f in os.listdir(input_folder) if f.endswith(('.jpeg', '.jpg', '.png'))])

    images_with_predictions = []
    for filename in image_filenames:
        image_path = os.path.join(input_folder, filename)
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(64, 64))
        input_arr = tf.keras.preprocessing.image.img_to_array(img)
        input_arr = np.expand_dims(input_arr, axis=0)
        predictions = cnn.predict(input_arr, verbose=0)
        result_index = np.argmax(predictions)
        predicted_class = class_names[result_index]
        predictions_list.append(predicted_class)
        images_with_predictions.append((url_for('static', filename=f'uploaded_images/{filename}'), predicted_class))

    available_ingredients, all_ingredients_available = check_ingredients(predictions_list, ingredient_names)

    session['images_with_predictions'] = images_with_predictions

    if all_ingredients_available:
        instructions = selected_dish['Instructions']
        sentences = [sentence.strip() for sentence in instructions.split('.') if sentence.strip()]
        return render_template('recipe.html', sentences=sentences,
                               ingredients_table=ingredients_df.to_html(index=False),
                               images_with_predictions=images_with_predictions)
    else:
        missing_ingredients = [ingredient for ingredient in ingredient_names if ingredient not in predictions_list]
        return render_template('missing.html', missing_ingredients=missing_ingredients,
                               images_with_predictions=images_with_predictions)


def plot_images(images_with_predictions):
    fig, axs = plt.subplots((len(images_with_predictions) // 3) + 1, 3, figsize=(15, 15))
    axs = axs.flatten()

    for ax, (filename, predicted_class) in zip(axs, images_with_predictions):
        img = tf.keras.preprocessing.image.load_img(filename)
        ax.imshow(img)
        ax.axis('off')
        ax.set_title(predicted_class)

    for ax in axs[len(images_with_predictions):]:
        ax.remove()

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    AIKitchen.run(debug=True)
