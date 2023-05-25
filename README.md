Model is ran through the group_displayer.py file. The file is ran through the command line with the following command:
```
python group_displayer.py
```
selections_pitch.csv should be a file in the same directory as group_displayer.py. The file should contain a first column with the name of the students, and 1 column per project. The pitched column should contain the index of the project that the student pitched, i.e. if Joao pitched the project in the first column, joao's pitched column should contain a 0. If the student did not pitch a project, this field should be left empty (see example in the repository).

The model will first minimize unhappiness by guranteeing at least a 2nd choice for everyone, and then set this solution as a baseline and try to maximise 1st choices. It is assumed that pitchers will place their project as their 1st choice, and if their project is picked, they are guaranteed to be in the group for it.
