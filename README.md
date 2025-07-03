# Research: Training model for automated detecting malicious NPM packages 
## Introduction
This is the source code for the research on the topic: Training model for automated detecting malicious NPM packages. In this project, I just built Centralized training architecture and used 9 different ML and DL model for training and evaluating process. 

The source code in this repository includes the entire implementation of my research. If you find it helpful for your own research, feel free to refer to it, but please make sure to cite and give my repo a star. It will motivate me a lot ☺️. Thank youuu!!!


## Requirements environmet
- Processing dataset step: I used VM linux environment to download npm packages and extract features . Because we have to work with malicious data, so that it will be better if we are careful in processing dataset.
- Training model step: You can run the programs in the source code on platforms such as Kaggle, Google Colab, or any other platform that supports running with GPU. As for me, I train locally on a WSL2 environment. About environment setup, i followed tutorial from this [repo](https://github.com/mahbub-aumi/tensorflow-cuda-wsl-ubuntu24.04) and [video](https://youtu.be/VOJq98BLjb8?si=fHDSOZ6bB1XfUJlB). You can follow this to set up the environment yourself. In addition, you’ll also need to run the following command to install the required libraries:
```
bash install.sh
```

## Dataset and Data processing
- There are two script in [Aggregate_Dataset](https://github.com/HocVoNgThai/Training-model-for-automated-detecting-malicious-NPM-packages/tree/main/Aggregate_Dataset) folder, you can download and put them into your project folder. Then run these two, they will be download and extract npm packages from nmpjs (benign packages) and DataDogs repository (malicious packages) into two different folders. The project folder should have the format like this:
```
/project-folder
|-- /dataset
|   |-- /malicious
|   |-- /benign
|-- download_benign.sh
|-- download_malicious.sh
```
- Then, using [feature_extractor.py](https://github.com/HocVoNgThai/Training-model-for-automated-detecting-malicious-NPM-packages/blob/main/Feature_Extractor/feature_extractor.py) to extract features from all of packages and make a file csv (with label 0: benign sample, label 1: malicious sample). But it at here:
```
/project-folder
|-- /dataset
|   |-- /malicious
|   |-- /benign
|-- download_benign.sh
|-- download_malicious.sh
|-- feature_extractor.py <--
```
- And running these commands:
```
sudo apt update
sudo apt install python3-venv
python3 -m venv myvenv
source venv/bin/activate
pip install esprima pandas numpy
python3 feature_extractor.py
```
- Then using this notebook [shuffle_dataset](https://github.com/HocVoNgThai/Training-model-for-automated-detecting-malicious-NPM-packages/blob/main/Feature_Extractor/shuffle_dataset.ipynb) or copying code to a python file and running to shuffle the samples in file npm_features_dataset.csv, so there will be not too many samples with the same label in a row. Shuffled dataset makes training proccess more effective.
- Datasets from this process are put at [Dataset](https://github.com/HocVoNgThai/Training-model-for-automated-detecting-malicious-NPM-packages/tree/main/Dataset) folder.
