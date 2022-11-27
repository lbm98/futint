import matplotlib.pyplot as plt


def main():
    with open('sta1.data', 'r') as fh:
        lines = fh.readlines()

        time_list = []
        rssi_list = []
        for data in lines:
            time, rssi = data.split(",")
            time_list.append(float(time))
            rssi_list.append(int(rssi))

        fig, ax = plt.subplots()
        ax.scatter(time_list, rssi_list)
        fig.savefig('sta1')
        plt.close()


if __name__ == '__main__':
    main()