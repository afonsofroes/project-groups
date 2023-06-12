import pandas as pd
from math import ceil
import numpy as np
from scipy.optimize import linprog

class GroupMaker:
    """Make groups based on preferences and display them nicely"""
    def __init__(self, max_size=4, min_size=3, x_c=1, custom_constraints=False, custom_objective=False):
        self.data_df = None
        self.result_df = pd.DataFrame()
        self.max_size = max_size
        self.min_size = min_size
        self.x_c = x_c
        self.col = None
        if custom_constraints:
            self.constraints = []
        else:
            self.constraints = [
                self._init_model,
                self._set_min_projects,
                self._set_group_size_range,
                self._prioritise_pitchers_in_pitched_projects,
                self._set_lockouts
            ]

        if custom_objective:
            self.objectives = []
        else:
            self.objectives = [
                self._objectives,
            ]

    def fit(self, data_df, verbose=False):

        if not self.constraints:
            raise Exception("No constraints defined")

        if not self.objectives:
            raise Exception("No objectives specified")

        self.data_df = data_df
        data_array = self.data_df.to_numpy()[:, 1:-2]
        self.n_projects = data_array.shape[1]
        self.n_students = data_array.shape[0]
        self.data_flat = data_array.reshape([self.n_students * self.n_projects])
        self.col = (self.n_students + 1) * self.n_projects + self.x_c

        for constraint in self.constraints:
            constraint()

        for objective in self.objectives:
            objective(verbose=verbose)


    def _init_model(self, **kwargs):
        # 1 project per person
        self.A = np.zeros([self.n_students, self.col])
        self.b = np.zeros(self.n_students)
        for i in range(self.n_students):
            self.A[i, i * self.n_projects : (i + 1) * self.n_projects] = 1
            self.b[i] = 1

        # project can only be selected once
        self.A_ub = np.zeros([self.n_projects, self.col])
        for i in range(self.n_projects):
            self.A_ub[i, self.col - self.x_c - self.n_projects + i] = 1
        self.b_ub = np.array([1] * self.n_projects)

        # selected project total
    def _set_min_projects(self):
        min_projects = ceil(self.n_students / self.max_size)
        temp = np.zeros([1, self.col])
        temp[0, -self.n_projects - self.x_c : -self.x_c] = -1
        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [-min_projects]])


        # selected project totals match selections
    def _set_group_size_range(self):
        temp = np.zeros([self.n_projects, self.col])
        for i in range(self.n_projects):
            for j in range(self.n_students):
                temp[i, j * self.n_projects + i] = -1
            temp[i, self.col - self.x_c - self.n_projects + i] = self.max_size
        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [self.max_size - self.min_size] * self.n_projects])

        temp = np.zeros([self.n_projects, self.col])
        for i in range(self.n_projects):
            for j in range(self.n_students):
                temp[i, j * self.n_projects + i] = 1
            temp[i, self.col - self.x_c - self.n_projects + i] = -self.max_size
        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [0] * self.n_projects])

        # if a pitched project is selected, the pitcher must be in the group
    def _prioritise_pitchers_in_pitched_projects(self):
        pitch_dict = {}
        for i, proj in self.data_df[["pitched"]].itertuples():
            if not type(proj)==int and proj.is_integer():
                pitch_dict[i] = int(proj)
        temp = np.zeros([len(pitch_dict), self.col])
        for i, (student_i, proj) in enumerate(pitch_dict.items()):
            temp[i, student_i * self.n_projects + proj] = 1
            temp[i, proj - self.n_projects - self.x_c] = -1

        self.A = np.concatenate([self.A, temp])
        self.b = np.concatenate([self.b, [0] * len(pitch_dict)])

    # if 2 people have the same number in the lockout column, they can't be in the same group
    def _set_lockouts(self):
        locked_groups = [
            tuple(self.data_df[self.data_df["lockout"] == lockout].index)
            for lockout in self.data_df["lockout"].unique()
            if lockout.is_integer()
        ]
        temp = np.zeros([len(locked_groups) * self.n_projects, self.col])
        for i, students in enumerate(locked_groups):
            for j in range(self.n_projects):
                for student in students:
                    temp[i * self.n_projects + j, student * self.n_projects + j] = 1
        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [1] * len(locked_groups) * self.n_projects])

    def _objectives(self, **kwargs):

        # minimax
        temp = np.zeros([self.n_students * self.n_projects, self.col])
        for i in range(self.n_students):
            for j in range(self.n_projects):
                temp[i * self.n_projects + j, i * self.n_projects + j] = self.data_flat[i * self.n_projects + j]
                temp[i * self.n_projects + j, self.col - self.x_c] = -1

        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [0] * self.n_students * self.n_projects])

        self.c = np.zeros(self.col)
        self.c[self.col - self.x_c] = 1

        try:
            result = linprog(self.c, A_eq=self.A, b_eq=self.b, A_ub=self.A_ub, b_ub=self.b_ub, integrality=1)
        except ValueError:
            raise ("Make sure you have the correct version of scipy")

        if not result.fun:
            raise Exception("No possible solution for current data. \
                            Check input data or reduce constraints")

        if kwargs.get("verbose"):
            print(
                "Optimal Value: ",
                round(result.fun, ndigits=2),
                "\nx Values: ",
                result.x,
                "\nNumber of iterations performed: ",
                result.nit,
                "\nStatus: ",
                result.message,
            )

        # setting best resultult as constraint
        temp = np.zeros([1, self.col])
        temp[0, self.col - self.x_c] = 1
        self.A_ub = np.concatenate([self.A_ub, temp])
        self.b_ub = np.concatenate([self.b_ub, [result.x[-1]]])

        # minimizing total pref
        self.c = np.concatenate([self.data_flat, [0] * (self.n_projects + 1)])
        self.result = linprog(self.c, A_eq=self.A, b_eq=self.b, A_ub=self.A_ub, b_ub=self.b_ub, integrality=1)

        if kwargs.get("verbose"):
            print(
                "Optimal value:",
                round(result.fun, ndigits=2),
                "\nx values:",
                result.x,
                "\nNumber of iterations performed:",
                result.nit,
                "\nStatus:",
                result.message,
            )

            print("Resultults: ")
            print(
                (result.x[: -self.n_projects - self.x_c] * self.data_flat)
                .reshape([self.n_students, self.n_projects])
                .astype(int)
            )

            print("\nChosen Projects: ")
            print(result.x[-self.n_projects - self.x_c : -self.x_c])

        self.result_df = pd.DataFrame(
            (result.x[: -self.n_projects - self.x_c] * self.data_flat)
            .reshape([self.n_students, self.n_projects])
            .astype(int)
        )



    def groups(self):
        """Displays the groups in a more readable format"""

        if self.result_df.empty:
            raise Exception("Run the fit method first")

        students_df = self.data_df["student"]
        self.result_df = pd.concat([students_df, self.result_df], axis=1)
        self.result_df.columns = self.data_df.drop(columns=["pitched", "lockout"]).columns
        self.result_df.set_index("student", inplace=True)

        display_df = self.result_df[self.result_df != 0].stack().reset_index()
        display_df.columns = ["student", "project", "pref"]
        display_df = display_df[["student", "project"]]
        display_df.set_index("student", inplace=True)
        display_df.sort_values(by=["project"], inplace=True)

        print(display_df)
