from joao_model import make_groups
import pandas as pd

n_projects = 5
n_students = 9
x_c = 1

data_df = pd.read_csv('selections.csv')
data = data_df.to_numpy()[:,1:].reshape([n_students*n_projects])

res = make_groups(data, n_projects, n_students, x_c)

res_df = pd.DataFrame((res.x[:-n_projects-x_c]*data).reshape([n_students,n_projects]).astype(int))
students_df = data_df['student']
res_df = pd.concat([students_df, res_df], axis=1)
res_df.columns = data_df.columns
res_df.set_index('student', inplace=True)

display_df = res_df[res_df != 0].stack().reset_index()
display_df.columns = ['student', 'project', 'pref']
display_df = display_df[['student', 'project']]
display_df.set_index('student', inplace=True)
display_df.sort_values(by=['project'], inplace=True)

print(display_df)
