import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
import sys
import os

def predict_unified(model_path, scaler_path, input_csv_path):

    print(f"Model: {model_path}")
    print(f"Input: {input_csv_path}")

    for f_path in [model_path, scaler_path, input_csv_path]:
        if not os.path.exists(f_path):
            print(f"Error: Not found file '{f_path}'")
            return

    try:
        scaler = joblib.load(scaler_path)
        print(f"Successfully loading scaler from '{scaler_path}'")
    except Exception as e:
        print(f"Error in loading scaler: {e}")
        return
        
    is_keras_model = False
    try:
        if model_path.endswith('.keras'):
            print("Loading model Deep Learning...")
            model = tf.keras.models.load_model(model_path)
            is_keras_model = True
        elif model_path.endswith('.joblib'):
            print("Loading model Machine Learning...")
            model = joblib.load(model_path)
        else:
            print(f"Error: Not support this model type '{os.path.splitext(model_path)[1]}'. Only support .keras và .joblib.")
            return
        print("Sunsuccessfully loading model")
    except Exception as e:
        print(f"Error in loading model: {e}")
        return


    df = pd.read_csv(input_csv_path)
    if df.empty:
        print("File input is empty.")
        return
    print(f"Loaded {len(df)} samples.")
    
    original_df = df.copy()
    features_df = df.drop(columns=['package_name'], errors='ignore')
    
    try:
        training_features = scaler.get_feature_names_out()
        features_df = features_df.reindex(columns=training_features, fill_value=0)
    except AttributeError:
        print("Warning: Unable to retrieve feature names from the scaler. Make sure dataset's columns match those used during training.")
        pass

    X_scaled = scaler.transform(features_df)
    
    if is_keras_model:
        if len(model.input_shape) == 3:
            print("  -> Detecting model CNN, reshaping dataset...")
            X_scaled = np.expand_dims(X_scaled, axis=2)
            
        probabilities = model.predict(X_scaled)
        predictions = (probabilities > 0.5).astype(int)
    else: 
        predictions = model.predict(X_scaled)
        
    print("Finish prediction.")


    original_df['label'] = predictions.flatten() 
    
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    input_base_name = os.path.splitext(os.path.basename(input_csv_path))[0]
    output_csv_path = f"../prediction_result/{input_base_name}_predictions_{model_name}.csv"
    
    original_df.to_csv(output_csv_path, index=False)
    print(f"Saved result to file: '{output_csv_path}'")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("\nUsage: python3 predict.py <path_to_model> <path_to_scaler.joblib> <path_to_input_features.csv>")
        print("Example (ML): python3 predict.py random_forest_model.joblib scaler.joblib ../features_extract/2025-07-03.csv")
        print("Example (DL): python3 predict.py cnn_model.keras scaler.joblib ../features_extract/2025-07-03.csv")
        sys.exit(1)
        
    model_file = sys.argv[1]
    scaler_file = sys.argv[2]
    input_file = sys.argv[3]
    
    predict_unified(model_file, scaler_file, input_file)
