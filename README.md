# Customized_AI_Kitchen

### Intel Project

## Overview
Customized_AI_Kitchen is a Flask-based web application that helps users identify ingredients in uploaded images and adjust recipe quantities based on the number of servings. The application uses a pre-trained TensorFlow model for image classification and processes recipes from a CSV dataset.

## Table of Contents
1. [Installation](#installation)
2. [Setup](#setup)
3. [Running the Application](#running-the-application)
4. [File Structure](#file-structure)

## Installation

### Clone the Repository
```sh
git clone https://github.com/HarshwardhanJain/Customized_AI_Kitchen.git
cd Customized_AI_Kitchen
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Setup

### Download the Dataset and Model

**1. Custom_Recipe_Dataset.csv:**
1. Ensure you have **Custom_Recipe_Dataset.csv**.
2. Place it in the directory **Customized_AI_Kitchen/**.

**2. Custom_Image_Classification_Trained_Model.h5:**
1. Ensure you have **Custom_Image_Classification_Trained_Model.h5**.
2. Place it in the directory **Customized_AI_Kitchen/**.

### Create Necessary Directories
```sh
mkdir -p Intel_Project/Intel_Customized_AI_Kitchen/static/uploaded_images
```

## Running the Application

### Run the Flask Application
```sh
python Customized_AI_Kitchen/AIKitchen.py
```
* **Access the application at http://127.0.0.1:5000/.**


## File Structure

```
Customized_AI_Kitchen/
│
├── Intel_Project/
│   └── Intel_Customized_AI_Kitchen/
│       ├── static/
│       │   └── uploaded_images/
│       ├── Custom_Recipe_Dataset.csv
│       └── Custom_Image_Classification_Trained_Model.h5
│
├── templates/
│   ├── index.html
│   ├── action.html
│   ├── upload.html
│   ├── recipe.html
│   └── missing.html
│
├── AIKitchen.py
├── requirements.txt
└── README.md
```

## Notes
* **Ensure all file paths are correct.**
