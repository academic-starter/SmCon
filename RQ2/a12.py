import numpy as np


def vargha_delaney_a12(x, y):
    """
    Compute Vargha and Delaney's A12 effect size.

    Parameters:
        x (list or array): Data from group X.
        y (list or array): Data from group Y.

    Returns:
        float: A12 effect size.
    """
    n_x = len(x)
    n_y = len(y)
    # Compute pairwise differences
    greater = sum(xi > yj for xi in x for yj in y)
    equal = sum(xi == yj for xi in x for yj in y)

    return (greater + 0.5 * equal) / (n_x * n_y)

# Example usage


issue_table_random = """
5	4	5	4	4	5
1	2	0	1	1	1
0	0	0	0	0	0
1	1	1	1	1	1
4	4	4	4	4	4
3	4	5	3	4	5
""".strip().split("\n")
issue_table_mbt = """
8	3	8	8	3	9
1	2	1	2	0	2
0	1	0	0	1	0
1	1	1	1	1	1
5	5	5	5	5	5
3	3	3	3	3	3
""".strip().split("\n")

for i in range(len(issue_table_random)):
    row_rand = issue_table_random[i]
    row_mbt = issue_table_mbt[i]

    a12_value = vargha_delaney_a12(
        list(map(int, row_mbt.strip().split("\t"))),  list(map(int, row_rand.strip().split("\t"))))
    print(f"Vargha and Delaney's A12: {a12_value}")


cov_table_random = """
69.09%	60.11%	70.27%	70.23%	70.44%	69.09%
22.09%	25.95%	23.26%	22.75%	25.77%	22.51%
24.61%	24.61%	24.54%	24.54%	24.61%	24.61%
22.36%	17.95%	18.47%	18.47%	17.51%	18.51%
45.71%	46.73%	47.89%	44.55%	47.89%	43.90%
41.98%	49.74%	53.61%	51.87%	53.25%	54.50%
""".strip().split("\n")
cov_table_mbt = """
79.62%	51.33%	81.98%	78.43%	51.50%	78.40%
13.81%	50.90%	33.10%	44.78%	38.14%	33.58%
22.76%	48.99%	18.90%	21.57%	33.74%	22.76%
35.49%	41.48%	43.60%	41.10%	41.44%	29.45%
50.09%	50.09%	50.09%	50.02%	50.16%	50.09%
32.99%	32.99%	32.99%	32.99%	32.99%	32.99%
""".strip().split("\n")

for i in range(len(cov_table_random)):
    row_rand = cov_table_random[i]
    row_mbt = cov_table_mbt[i]

    a12_value = vargha_delaney_a12(
        list(map(lambda item: float(item.replace('%', 'e-2')), row_mbt.strip().split("\t"))),  list(map(lambda item: float(item.replace('%', 'e-2')), row_rand.strip().split("\t"))))
    print(f"Vargha and Delaney's A12: {a12_value}")
