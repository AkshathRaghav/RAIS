# Reproducible Artificial Intelligence Software 

<div align="center">
  <img src="https://drive.google.com/thumbnail?id=1rz_bIpkFOfe4uZ2AKzwq29Am9wC6YFOv&sz=h2000" alt="maskformer" style="width: 80%;"/>
  <p>This repository contains the source code I wrote for the RAIS project at the CVES group under [Prof. Lu](https://yhlu.net/). It was used in my report [here](https://akshathraghav.github.io/projects/rais/).</p>
</div>


# Overview 
This project aimed to investigate the methodologies to create Reproducible AI Software (called **RAIS**). This project will identify a list of essential factors that may contribute (or hurt) reproducibility. Based on this list, RAIS will evaluate reproducibility by examining software repositories and their history to detect the events when software’s reproducibility start declining and issue alerts. RAIS will use large language models (LLMs) to analyze documentations, comments, source code, and reports in order to understand the contents, validate consistency, and suggest improvements. 

## Getting Started

### Cloning the Repository
1. First, clone the RAIS repository to your local machine using the following command:
    ```bash
    git clone https://github.com/AkshathRaghav/RAIS.git
    ```

### Setting Up a Python Virtual Environment
2. Navigate to the cloned repository:
    ```bash
    cd RAIS
    ```
3. Create a Python virtual environment (venv):
    ```bash
    python3.9 -m venv venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

### Installing Dependencies
```bash
make install
```

## Getting Data from Google Cloud

### Downloading the Data
- Locate the [depot/](https://drive.google.com/drive/folders/1-p7hZDR00mWtLYiR2zxYTQiNcLH1JBlZ) folder. Download it as a zipped file. 
  Extract it using: 
  ```bash 
  unzip depot.zip 'depot/*' -d .        
  ```
<b>OR</b>
- Download the [.tar.gz](). 
  Extract it using: 
  ```bash 
  tar -xzvf depot.tar.gz 
  ```

## Data Overview
The extracted depot follows this structure. If you do not want to use the data above, you can initialize it using the Depot class. More information below. 
```
  # - depot/
  #   - papers/
  #     - authors/
  #   - repository/
  #     - owner/
  #     - organization/ 
  #     - member/
```
(The goal was to enable abstractability of previously scraped data!)

1. `depot/mapping.json` contains the file_paths of everything related to an ML project
```json
  {
    "https://arxiv.org/abs/2305.19256": {
      "paper": "../depot/papers/2305.19256/Ambient Diffusion: Learning Clean Distributions from Corrupted Data.pdf",
      "paper_metadata": "../depot/papers/2305.19256/metadata.json",
      "authors": [
        "../depot/papers/authors/Giannis Daras.json",
        "../depot/papers/authors/Kulin Shah.json",
        "../depot/papers/authors/Yuval Dagan.json",
        "../depot/papers/authors/Aravind Gollakota.json",
        "../depot/papers/authors/Alexandros G. Dimakis.json",
        "../depot/papers/authors/Adam Klivans.json"
      ]
    },
    "giannisdaras/ambient-diffusion": {
      "branch": "main",
      "tree": "../depot/repository/giannisdaras_ambient-diffusion/tree.json",
      "repo_metadata": "../depot/repository/giannisdaras_ambient-diffusion/metadata.json",
      "commit_history": "../depot/repository/giannisdaras_ambient-diffusion/commit_history.json",
      "star_history": "../depot/repository/giannisdaras_ambient-diffusion/star_history.json",
      "tree_formatted": "../depot/repository/giannisdaras_ambient-diffusion/tree_formatted.txt",
      "owner_metadata": "../depot/repository/owner/giannisdaras.json",
      "organization_metadata": null,
      "members_metadata": []
    }
  },
  ....
```
2. `depot/repostory` will contain folders in the form of 
    - `{owner_name}_{repo_name}`/
    - `organization`/ -> Induvidual organization data
    - `members`/ -> All members data across projects
    - `owner`/ -> Data of owners
3. `depot/paper` will contain folders in the form of 
    - `{doi}`/
    - `authors`/ -> Induvidual author metadata 

## Codebase Overview

1. Under `src/`, I've listed some testing files under `experiment.*` alias. You can use those to get started. 
2. Under `src/backend/`, I've modularized the component files.
    - `evaluator/` contains the files for extracting all data 
    - `tools/` contains other files for functions like logging and storing
3. `src/backend/evaluator/github/github.py` contains extra code and functions which can be used on a Github object to 
    - Find any files 
    - Extract the code of the files from the web 
    - Extract all the lexical components of python files 
    - Extract Markdown file headers
    - etc. 
  I'm using them for evaluating the pipeline. 
4. `src/backend/evaluator/huggingface` is not complete. It can only extract file tree for now. 
5. `src/backend/evaluator/paper` gets all the metadata I found important. A lot of the extracted data might be overheads unrelated to a specific project being scraped, but I believe there could be a use for them later. 

