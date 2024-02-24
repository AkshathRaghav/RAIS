# Reproducible Artificial Intelligence Software 

<div align="center">
  <img src="https://drive.google.com/thumbnail?id=1rz_bIpkFOfe4uZ2AKzwq29Am9wC6YFOv&sz=w1000" alt="maskformer" style="width: 80%;"/>
</div>

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
5. Install the required Python packages from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Getting Data from Google Cloud

### Downloading the Data
6. Locate the [depot/](https://drive.google.com/drive/folders/1-p7hZDR00mWtLYiR2zxYTQiNcLH1JBlZ) folder under 'Akshath Raghav R'/. Download it as a zipped file. 
7. Extract it using: 
  ```bash 
  unzip depot.zip 'depot/*' -d .        
  ```

## Using the data 
1. `depot/mapping.json` contains the file_paths of everything related to a project 
2. `depot/repostory` will contain folders in the form of 
  - `{owner_name}_{repo_name}`/
  - `organization`/ -> Induvidual organization data
  - `members`/ -> All members data across projects
  - `owner`/ -> Data of owners
  The goal was to abstract the metadatas so that they can be queried induviudally and used to avoid unneccessay scraping 
  (I've not implemented that part fully yet, so it will scrape some data pointlessly.)
3. `depot/paper` will contain folders in the form of 
  - `{doi}`/
  - `authors`/ -> Induvidual author metadata 

## Using the code

1. Under src/, I've listed some testing files under 'experiment.*' alias. You can use those to get started. 
2. Under src/backend/, I've modularized the component files.
    - evaluator/ contains the files for extracting 
    - tools/ contains other files for functions like logging and storing
3. src/backend/evaluator/github/github.py contains extra code and functions which can be used on a Github object to 
  - Find any files 
  - Extract the code of the files from the web 
  - Extract all the lexical components of python files 
  - Extract Markdown file headers
  - etc. 
  I'm using them for evaluating the pipeline. 
4. src/backend/evaluator/huggingface is not complete. It can only extract file tree for now. 
5. src/backend/evaluator/paper gets all the metadata I found important. A lot of the extracted data might be overheads unrelated to a specific project being scraped, but I believe there could be a use for them later. 
