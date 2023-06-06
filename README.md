### Setup

Minimum python version: 3.8

Tested up to 3.11

Install dependencies by running the following command

```
make install
```
OR

```
pip install -r requirements.txt
```

### Usage

Model is ran through the group_displayer.py file. The file is ran through the command line with the following command while in the project directory:
```
make
```
OR
```
python group_displayer.py
```
'selections_pitch.csv' should be a file in the same directory as group_displayer.py. The file should contain a first column with the name of the students, and 1 column per project. The 'pitched' column should come last, and it should contain the index of the project that the student pitched, i.e. if Joao pitched the first project listed (2nd column overall), Joao's pitched column should contain a 0 (for index 0 of the list of projects). If the student did not pitch a project, this field should be left empty (see 'selections_pitch.csv' example in the repository).

The model will first minimize unhappiness by guaranteeing at least a 2nd choice for everyone, and then set this solution as a baseline and try to maximise 1st choices. It is assumed that pitchers will place their project as their 1st choice, and if their project is picked, they are guaranteed to be in the group for it.
