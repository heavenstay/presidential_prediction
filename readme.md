# Presidential Prediction Repository

This repository contains a Python project that aims to predict the results of presidential elections.

## Structure

The repository is structured as follows:

- `cleaned_data`: This directory contains cleaned data files used for the prediction. The data includes information about candidates, unemployment rates, company failures, crime rates, and purchasing power.
- `fusioned_data`: This directory contains the results of the data fusion process.
- `script`: This directory contains Python scripts for data fusion and machine learning.

## Scripts

### fusion_data.py

This script is responsible for fusing the data from different sources. It reads the data from the `cleaned_data` directory, processes it, and stores the results in the `fusioned_data` directory. The script performs the following steps:

1. Reads the election results data for different years and departments.
2. Merges the election results with the candidates' data.
3. Calculates the average purchasing power, crime rate, unemployment rate, and the number of company failures for each year.
4. Determines the winner of the first and second rounds of the election for each year and department.
5. Writes the results to an Excel file and a CSV file.

Please note that this is a high-level overview of the repository. For more detailed information, you can consult the following doc: https://drive.google.com/file/d/1rC7lmlCoyYjk6slY7s8elGCipKhU1KQ8/view?usp=sharing. 
