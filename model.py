"""Model Joao made for making groups based on preferences"""
from math import ceil
import numpy as np
from scipy.optimize import linprog
import pandas as pd


def make_groups(data_df, max_size=4, min_size=3):
    """Make groups based on preferences"""
    # x_c is the number of extra columns for any necessary processing
    x_c = 1

    data_array = data_df.to_numpy()[:, 1:-2]
    n_projects = data_array.shape[1]
    n_students = data_array.shape[0]
    data_flat = data_array.reshape([n_students * n_projects])

    min_projects = ceil(n_students / max_size)

    col = (n_students + 1) * n_projects + x_c

    A = np.zeros([n_students, col])
    b = np.zeros(n_students)

    A_ub = np.zeros([n_projects, col])
    b_ub = np.array([max_size] * n_projects)

    # 1 project per person
    for i in range(n_students):
        A[i, i * n_projects : (i + 1) * n_projects] = 1
        b[i] = 1

    # max 4 people per project
    for i in range(n_projects):
        for j in range(n_students):
            A_ub[i, j * n_projects + i] = 1

    # selected project total
    temp = np.zeros([1, col])
    temp[0, -n_projects - x_c : -x_c] = -1
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [-min_projects]])

    # project can only be selected once
    temp = np.zeros([n_projects, col])
    for i in range(n_projects):
        temp[i, col - x_c - n_projects + i] = 1
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [1] * n_projects])


    # selected project totals match selections
    temp = np.zeros([n_projects, col])
    for i in range(n_projects):
        for j in range(n_students):
            temp[i, j * n_projects + i] = -1
        temp[i, col - x_c - n_projects + i] = max_size
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [max_size-min_size] * n_projects])

    temp = np.zeros([n_projects, col])
    for i in range(n_projects):
        for j in range(n_students):
            temp[i, j * n_projects + i] = 1
        temp[i, col - x_c - n_projects + i] = -max_size
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [0] * n_projects])

    # if a pitched project is selected, the pitcher must be in the group
    pitch_dict = {}
    for i, proj in data_df[["pitched"]].itertuples():
        if not type(proj)==int and proj.is_integer():
            pitch_dict[i] = int(proj)
    temp = np.zeros([len(pitch_dict), col])
    for i, (student_i, proj) in enumerate(pitch_dict.items()):
        temp[i, student_i * n_projects + proj] = 1
        temp[i, proj - n_projects - x_c] = -1

    A = np.concatenate([A, temp])
    b = np.concatenate([b, [0] * len(pitch_dict)])

    # if 2 people have the same number in the lockout column, they can't be in the same group
    locked_pairs = [
        tuple(data_df[data_df["lockout"] == lockout].index)
        for lockout in data_df["lockout"].unique()
        if lockout.is_integer()
    ]
    temp = np.zeros([len(locked_pairs) * n_projects, col])
    for i, (student_1, student_2) in enumerate(locked_pairs):
        for j in range(n_projects):
            temp[i * n_projects + j, student_1 * n_projects + j] = 1
            temp[i * n_projects + j, student_2 * n_projects + j] = 1
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [1] * len(locked_pairs) * n_projects])

    # minimax
    temp = np.zeros([n_students * n_projects, col])
    for i in range(n_students):
        for j in range(n_projects):
            temp[i * n_projects + j, i * n_projects + j] = data_flat[i * n_projects + j]
            temp[i * n_projects + j, col - x_c] = -1

    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [0] * n_students * n_projects])

    c = np.zeros(col)
    c[col - x_c] = 1

    try:
        result = linprog(c, A_eq=A, b_eq=b, A_ub=A_ub, b_ub=b_ub, integrality=1)
    except ValueError:
        raise ("Make sure you have the correct version of scipy")

    if not result.fun:
        raise Exception("No possible solution for current data. "+
                        "Check input data or reduce constraints")


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
    temp = np.zeros([1, col])
    temp[0, col - x_c] = 1
    A_ub = np.concatenate([A_ub, temp])
    b_ub = np.concatenate([b_ub, [result.x[-1]]])

    # minimizing total pref
    c = np.concatenate([data_flat, [0] * (n_projects + 1)])
    result = linprog(c, A_eq=A, b_eq=b, A_ub=A_ub, b_ub=b_ub, integrality=1)

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
        (result.x[: -n_projects - x_c] * data_flat)
        .reshape([n_students, n_projects])
        .astype(int)
    )

    print("\nChosen Projects: ")
    print(result.x[-n_projects - x_c : -x_c])

    result_df = pd.DataFrame(
        (result.x[: -n_projects - x_c] * data_flat)
        .reshape([n_students, n_projects])
        .astype(int)
    )

    return result_df
