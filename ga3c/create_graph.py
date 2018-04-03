import matplotlib.pyplot as plt

def time_passed(start_time, cur_time):
    c_time = cur_time.split(':')
    c_time = list(map(int, c_time))
    start_time = list(map(int, start_time))
    for i in reversed(range(len(c_time))):
        if c_time[i] < start_time[i]:
            if i > 0:
                c_time[i-1]-=1
                c_time[i]+=60
            else:
                c_time[i]+=24
    time_diff = c_time[2]-start_time[2]
    time_diff+=((c_time[1]-start_time[1])*60)
    time_diff+=((c_time[0]-start_time[0])*60*60)
    print(time_diff)
    return time_diff

def main():
    x, y, z = [], [], []
    with open('./results.txt', 'r') as f:
        start_time = None
        w = 0
        for line in f:
            temp = line.split(',')
            time = temp[0].split()
            score = temp[1][1:]
            length = temp[2][1:]
            if start_time == None:
                start_time = time[1].split(':')
                time_diff = 0
            else:
                time_diff = time_passed(start_time, time[1])
            x.append(time_diff)
            y.append(int(score))
            z.append(int(length))
            w+=1

    lists = sorted(zip(*[x, y]))
    new_x, new_y = list(zip(*lists))
    lists = sorted(zip(*[x, z]))
    new_x, new_z = list(zip(*lists))
    plt.figure(1)                # a second figure
    plt.plot(new_x, new_y)
    plt.xlabel('Time')
    plt.ylabel('Reward (int)')

    plt.figure(2)                # a second figure
    plt.plot(new_x, new_z)
    plt.xlabel('Time')
    plt.ylabel('Episode Length')
    plt.show()

if __name__ == '__main__':
    main()
