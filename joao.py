import numpy as np
from scipy.optimize import linprog
import pandas as pd

n_p = 5
n_s = 9

x_c = 1
col = (n_s+1)*n_p+x_c

data = pd.read_csv('groups_test_vals.csv').to_numpy()[:,1:].reshape([n_s*n_p])

A = np.zeros([n_s,col])
b = np.zeros(n_s)

#one project per person
for i in range(n_s):
    A[i,i*n_p:(i+1)*n_p] = 1
    b[i] = 1

#max 3 people per project
A_ub = np.zeros([n_p,col])
b_ub = np.array([3]*n_p)
for i in range(n_p):
    for j in range(n_s):
        A_ub[i,j*n_p+i] = 1
        
#selected project total to 9
temp = np.zeros([1,col])
temp[0,-n_p-x_c:-x_c] = 1
A = np.concatenate([A, temp])
b = np.concatenate([b,[3]])

#selected project max 3       
temp = np.zeros([n_p,col])
for i in range(n_p):
    temp[i,col-x_c-n_p+i] = 1
A_ub = np.concatenate([A_ub,temp])
b_ub = np.concatenate([b_ub,[1]*n_p])


#select project totals match selections
temp = np.zeros([n_p,col])
for i in range(n_p):
    for j in range(n_s):
        temp[i,j*n_p+i] = 1
    temp[i,col-x_c-n_p+i] = -3
A = np.concatenate([A, temp])
b = np.concatenate([b,[0]*n_p])

#minimax pref
temp = np.zeros([n_s*n_p,col])
for i in range(n_s):
    for j in range(n_p):
        temp[i*n_p+j, i*n_p+j] = data[i*n_p+j]
        temp[i*n_p+j,col-x_c] = -1

A_ub = np.concatenate([A_ub,temp])
b_ub = np.concatenate([b_ub,[0]*n_s*n_p])

c = np.zeros(col)
c[col-x_c] = 1

res = linprog(c, A_eq=A, b_eq=b, A_ub=A_ub, b_ub=b_ub,integrality=1)

print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)

#setting best result as constraint
temp = np.zeros([1,col])
temp[0,col-x_c] = 1
A_ub = np.concatenate([A_ub,temp])
b_ub = np.concatenate([b_ub,[res.x[-1]]])

#minimizing total pref
c = np.concatenate([data,[0]*(n_p+1)])*-1

res = linprog(c, A_eq=A, b_eq=b, A_ub=A_ub, b_ub=b_ub,integrality=1)


print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)

print("results")
print((res.x[:-n_p-x_c]*data).reshape([n_s,n_p]).astype(int))


print("\nchosen projects")
print(res.x[-n_p-x_c:-x_c])