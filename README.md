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
"selections_pitch.csv" should be a file in the same directory as group_displayer.py. The file should contain a first column with the name of the students, and 1 column per project (see "selections_pitch.csv" example in the repository).

The "pitched" column should come next, and it should contain the index of the project that the student pitched, i.e. Victoria pitched the "Sexual Health Clinics" project (7th project, 8th column overall), Victoria's pitched column should contain a 6 (for index 6 of the list of projects). If the student did not pitch a project, this field should be left empty.
## Data format
"selections_pitch.csv" should be a file in the same directory as group_displayer.py. The file should contain a first column with the name of the students, and 1 column per project (see "selections_pitch.csv" example in the repository).

The "lockout" column makes it so that 2 people with the same lockout number cannot be in the same group. An empty field indicates this constraint will not be applied. In the example, Eitenne will never be in Victoria's group regardless of their preferences.
The "pitched" column should come next (oenultimate column), and it should contain the index of the project that the student pitched, i.e. Victoria pitched the "Sexual Health Clinics" project (7th project, 8th column overall), Victoria's pitched column should contain a 6 (for index 6 of the list of projects). If the student did not pitch a project, this field should be left empty.

The "lockout" column comes last. It makes it so that 2 people with the same lockout number cannot be in the same group. An empty field indicates this constraint will not be applied to the student. In the example, Eitenne will never be in Victoria's group regardless of their preferences, but everyone else has the possibility of working with any other student.

## About the model
The model will first minimize unhappiness by guaranteeing at least a 2nd choice for everyone, and then set this solution as a baseline and try to maximise 1st choices. It is assumed that pitchers will place their project as their 1st choice, and if their project is picked, they are guaranteed to be in the group for it.
