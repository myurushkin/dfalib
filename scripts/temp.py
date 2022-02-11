import numpy as np

def custom_trapz(y, x):
    print(y)
    print(x)

    s1 = (y[:-1, :] + y[1:, :])
    s2 = y[:, :-1] + y[:, 1:]
    val = (s1[:,:-1] + s2[:-1, :])/4.0

    x1 = x[:-1, :] - x[1:, :]
    x2 = x[:, :-1] - x[:, 1:]
    s = x1[:,:-1] * x2[:-1, :]
    return np.sum(val * s)


if __name__ == "__main__":
    x = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
    y = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    print(x.shape)
    print(y)
    print(custom_trapz(y, x))