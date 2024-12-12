class Dataset:
    def __init__(self):
        self.dataset = {"acc_x": [], "acc_y": [], "acc_z": [], "bvp": [], "eda": [], "temp": []}

    def add(self, acc_x, acc_y, acc_z, bvp, eda, temp):
        self.dataset["acc_x"].append(acc_x)
        self.dataset["acc_y"].append(acc_y)
        self.dataset["acc_z"].append(acc_z)
        self.dataset["bvp"].append(bvp)
        self.dataset["eda"].append(eda)
        self.dataset["temp"].append(temp)

    def to_dict(self):
        return self.dataset