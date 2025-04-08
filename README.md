# NMDID

```
conda create -n NMDID python=3.10 -y
conda activate NMDID
pip3 install -r requirements.txt
```

## 0. Download NMDID dataset
```
brew install --cask chromedriver
which chromedriver
```

## 1. Unzip NMDID dataset
```
python3 1_unzip.py
```

## 2. Convert dcm to nii.gz
```
pip3 install dcm2niix
python3 2_dcm2nii.py
```