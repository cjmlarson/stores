import csv

import numpy as np


# path-following linear program solver
def solve(A, b, c):
    # set according to simulation
    delta = 1 / 10
    r = 9 / 10
    max_iterations = 1000

    # options
    text_output = False

    n = len(c)  # number of primal variables
    m = len(b)  # number of primal constraints

    x = np.ones(n)  # primal variables
    w = np.ones(m)  # primal slacks

    y = np.ones(m)  # dual variables
    z = np.ones(n)  # dual slacks

    # printing
    np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
    if text_output:
        print("Iteration\tPrimal Feasibility\tDual Feasibility\tComplementarity\t\tValues of x")

    for i in range(max_iterations):
        rho = b - A.dot(x) - w
        sigma = c - A.transpose().dot(y) + z
        gamma = z.transpose().dot(x) + y.transpose().dot(w)
        mu = delta * gamma / (n + m)

        # right hand side
        rhs = np.block([rho,
                        sigma,
                        np.repeat(mu, n) - x * z,
                        np.repeat(mu, m) - np.multiply(y, w)
                        ])

        # left hand side (big matrix)
        lhs = np.block([
            [A, np.identity(m), np.zeros((m, m)), np.zeros((m, n))],
            [np.zeros((n, n)), np.zeros((n, m)), A.transpose(), -1 * np.identity(n)],
            [np.diag(z), np.zeros((n, m)), np.zeros((n, m)), np.diag(x)],
            [np.zeros((m, n)), np.diag(y), np.diag(w), np.zeros((m, n))]
        ])

        # solve the system of linear equations
        solution = np.linalg.solve(lhs, rhs)

        # deltas
        dx = solution[0:n]
        dw = solution[n:n + m]
        dy = solution[n + m:n + 2 * m]
        dz = solution[n + 2 * m:]

        # theta
        ratio = -1 * min(np.block([dx / x, dw / w, dy / y, dz / z]))
        theta = min(r / ratio, 1)

        # adjust variables
        x += theta * dx
        y += theta * dy
        w += theta * dw
        z += theta * dz

        # print results
        if text_output:
            print("%d\t\t\t%1.2e\t\t\t%1.2e\t\t\t%1.2e\t\t\t" %
                  (i + 1, np.linalg.norm(rho), np.linalg.norm(sigma), gamma), x)

        # stopping conditions
        max_iterations -= 1
        if mu < 1e-9:
            break
        if np.linalg.norm(rhs) < 1e-9:
            break

    # print result
    # print("\nObjective: ")
    # print(x.dot(c))
    # print("Weights:\n", np.multiply(x, c)*-1)
    # print("w: ", w)
    # print("\nDual solution:\ny: ", y)
    # print("z: ", z)

    # find best performing store
    scores = A.dot(x)*-1
    best_store = 0
    min_score = 2
    for i in range(len(scores)):
        if scores[i] < min_score:
            min_score = scores[i]
            best_store = i+1

    # return efficiency and constraining store
    return [round(1 / (x.dot(c) * -1), 2), best_store]


# read in data
data = list(csv.reader(open('annualized.csv')))
headers = data.pop(0)
num_stores = len(data)

# find list of states
states = []
for store in data:
    if store[1] not in states:
        states.append(store[1])

# set up "big matrix"
all_coefs = []
for row in data:

    coefs = [float(row[3]) / float(row[2]), float(row[4]) / float(row[2]), float(row[5]) / float(row[2]),
             float(row[6]) / float(row[2])]

    for j in range(len(states)):
        if row[1] == states[j]:
            coefs.append(10**7/float(row[2]))
        else:
            coefs.append(0)

    all_coefs.append(coefs)

A = np.array(all_coefs) * (-1)
b = np.ones(num_stores) * (-1)

# solve system
to_csv = [["Store number", "Efficiency", "Best comparison"]]

for i in range(num_stores):
    print("Calculating %.2f%%" % (100*i/num_stores))
    c = np.array(all_coefs[i]) * -1
    output = solve(A, b, c)
    output.insert(0,int(data[i][0]))
    to_csv.append(output)

# output to csv
csv.writer(open('efficiency.csv', mode='w', newline='')).writerows(to_csv)
