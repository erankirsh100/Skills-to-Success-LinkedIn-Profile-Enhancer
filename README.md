# Skills-to-Success-LinkedIn-Profile-Enhancer 🚀

## Overview

This repository contains a series of Jupyter notebooks aimed at enhancing LinkedIn profiles by analyzing job-related data, extracting relevant skills, and evaluating skill improvements. The workflow is divided into three main steps: clustering job-related data using KMeans, retrieving relevant skills, and evaluating skill enhancements.

---
## 1. 🕷️ Scraping Indeed 
### What the notebook does:
The notebook scrapes job postings from Indeed for companies that are in the companies_to_scarpe.csv file.
Then, it generates skills using calls to google genai api and saves the results.
Afterward, it does the same thing to a dataset of job postings from kaggle (also from Indeed) and saves the results.
Finally, it merges the two datasets and saves the final dataset.

### What you need to run the notebook:
You will a need a companies_to_scarpe.csv file with the following column - 'name'.
The notebook will scrape the jobs those companies have posted on Indeed and save them in a csv file.

Additionally, you will need to have the indeed dataset from kaggle named 'Indeed_kaggle_1.csv' in the same directory as the notebook.

#### links to the datasets needed: 

technion onedrive link for the companies_to_scarpe.csv file - https://technionmail-my.sharepoint.com/:f:/g/personal/eran_kirsh_campus_technion_ac_il/Emh99N3eut5Jr2uaEQAGGtUBTXme1J2PHpTP1nKvTg79yw?e=BdOysQ

technion onedrive link kaggle dataset - https://technionmail-my.sharepoint.com/:x:/r/personal/eran_kirsh_campus_technion_ac_il/Documents/data_files_project_Skills_to_Success_LinkedIn_Profile_Enhancer/Indeed_kaggle_1.csv?d=w233f401a0d0441a6ab1d6c322eb22a5d&csf=1&web=1&e=7htKq4


#### Things to change in the notebook:

1. In cell 5, insert your bright data name and password in the designated places.

```python
  # HERE INSERT BRIGHT DATA CREDENTIALS
  AUTH = 'username:password'

  SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'
  ```

2. in cell 20 change add your own api lists to google genai api.

```python
  # INSERT A LIST OF API KEYS TO GENAI HERE
  API_LIST = ['']
  ```

if you did all of the above you should be able to run all the cells in the notebook consecutively and get the final dataset.

## 2. 🧩 KMeans Communities and Data Analysis

**File:** `Kmeans_comunities_and_data_Analysis.ipynb`

### Purpose

This notebook consists of two parts:

1. **Cluster Recommendations:** Supplies the user with cluster suggestions, including potential courses, leader profiles to emulate, jobs to aspire to, and relevant companies.
2. **Cluster Comparison and Data Analysis:** Compares different clusters using word clouds and various visualizations, such as missingness and input length of categories against LinkedIn follower count bins (0-100, 101-200, etc.), showing that accounts with more followers tend to have less missingness and more detailed content, which may correlate with higher quality content. The results help categorize job positions and their associated skills.

### Data Used

- LinkedIn company profiles dataset
- LinkedIn user profiles dataset

### What to Change or Add

- Change dataset paths to match the location of your LinkedIn data:
  ```python
  companies = spark.read.parquet('/dbfs/linkedin_train_data')
  profiles = spark.read.parquet('/dbfs/linkedin_people_train_data')
  ```
  Ensure these paths point to the correct files in your environment.
- Modify the number of clusters (`n_clusters`) to optimize grouping.
- To get the cluster suggestions, update the function call by replacing the placeholder with your actual profile ID. The cluster suggestions include:

  - **List of courses that the user could take or learn**
  - **Leader profiles that can be emulated**
  - **Jobs to aspire to**
  - **Companies and job opportunities**
  ```python
  get_cluster_values('enter-your-id-here')
  ```
- To compare different clusters, update the cluster IDs in the word cloud visualization section:
  ```python
  cluster_id_1 = 70
  cluster_id_2 = 103
  ```
  Change these values to other cluster IDs to explore different comparisons.
- Update preprocessing steps based on the dataset used.
- Adjust visualization parameters to better represent clusters.

---

## 3. 🛠️ Skills Retrieval

**File:** `Skills_retrieval.ipynb`

### Purpose

This notebook retrieves skills related to job postings and specific roles. The extracted skills are used to refine LinkedIn profiles for better alignment with job market demands.

### Data Used

- Output from the KMeans clustering step
- Job descriptions dataset
- Skills taxonomy (optional)

### What to Change or Add

- Update retrieval methods to improve skill matching accuracy.
- Modify filtering criteria to exclude irrelevant or redundant skills.
- Adjust text processing techniques (e.g., stemming, lemmatization) to enhance results.
- Ensure correct linkage with the clustering results from the previous step.

---

## 4. 📊 Evaluation File

**File:** `Evaluation_file.ipynb`

### Purpose

This notebook evaluates the extracted skills against job requirements to measure their relevance and effectiveness in enhancing LinkedIn profiles.

### Data Used

- Table output from the `Skills_retrieval` step containing user summaries, required skills, and tools.

### What to Change or Add

- Add your API key in the code snippet: `api = 'put your API key here'`.
- Specify the correct paths to the model-reserved data from `Skills_retrieval`:
  ```python
  path_without_abouts = '/content/all_test_users.csv' # or change to the path of the file without abouts.
  path_with_abouts = '/content/test_users_with_about.csv' # or change to the path of the file with abouts.
  ```
- Run all cells in the notebook.
- Execute the cells containing the `Evaluation` function to obtain results.
- Modify the parameters of `Evaluation` to conduct different experiments.

---

## 📖 Usage Instructions

1. Run `Kmeans_comunities_and_data_Analysis.ipynb` to cluster job-related data.
2. Use `Skills_retrieval.ipynb` to extract relevant skills from clustered job roles.
3. Execute `Evaluation_file.ipynb` to assess the extracted skills' relevance.

Ensure all required datasets are correctly linked and update parameters as needed to refine results.

---

## 📦 Dependencies

Make sure to install the necessary Python libraries before running the notebooks:

```bash
pip install pandas numpy scikit-learn seaborn matplotlib nltk spark scipy google-generativeai
```

Additionally, the following libraries should be imported in the notebooks:

```python
import pandas as pd
import re
import google.generativeai as genai
import os
import time
from scipy.stats import wilcoxon
import numpy as np
```

