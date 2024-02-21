


# What defines a good quality score? 

### 1. Standard Directory Layouts

This would involve comparing a repository's layout against standard structures for similar projects. 
a. Lack of objectivity
b. Too vague 

### 2. Readability and Naming Conventions

Evaluate the clarity of naming conventions and file names. Folder and file names must have a purpose. 
  - A directory named /utils should contain utility scripts or modules.
  - File names like user_authentication.py clearly indicate purpose.

### 3. Guidelines Quality 

Precense of files like 'README', 'CONTRIBUTING', 'MODELZOO', 'METRICS'. This shows that the repo owners gave the reproducibility and impact of their repository importance. 

### 4. Dependency Management 

'package.json', 'requirements.txt', etc. 

Another consideration would be checking the languages present in the repo and expecting certain config files to be there. This requires a comprehensive list of expected configurations. 

### 5. Code Organization 

Review how code is organized within the repository, including the use of subdirectories for modularization and separation of concerns.

### 6. Presence of Automated Tests

People who add unit tests to the repositories make me weak in the knees. Automatic +10 points \s. 

### 7. Linter Configuration 

We'd need a comprehensive list of files for different languages which define a 'linter' setup. Example, 'pylintrc' is what is used for Python codebases and 'eslintrc' is what is used for Java codebases. 

### 8. LICENSE and CITATION 

I'd define this metric as the 'highest standard'. Is it the most important? No, but it gets huge brownie points. 