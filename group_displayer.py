from joao_model import make_groups
import pandas as pd


x_c = 1

data_df = pd.read_csv('selections_pitch.csv')
data_array = data_df.to_numpy()[:,1:-1]
n_projects = data_array.shape[1]
n_students = data_array.shape[0]
data = data_array.reshape([n_students*n_projects])

res = make_groups(data, n_projects, n_students, x_c)

res_df = pd.DataFrame((res.x[:-n_projects-x_c]*data).reshape([n_students,n_projects]).astype(int))
students_df = data_df['student']
res_df = pd.concat([students_df, res_df], axis=1)
res_df.columns = data_df.drop(columns=['pitched']).columns
res_df.set_index('student', inplace=True)

display_df = res_df[res_df != 0].stack().reset_index()
display_df.columns = ['student', 'project', 'pref']
display_df = display_df[['student', 'project']]
display_df.set_index('student', inplace=True)
display_df.sort_values(by=['project'], inplace=True)

print(display_df)