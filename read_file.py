import os
import datetime

def get_date_time():
    today = str(datetime.datetime.today())
    date = today.split(' ')[0]
    time = today.split(' ')[1].split('.')[0]
    # print(date)
    # print(time)
    return (date, time)

def get_data_from_file(date, time):
    total = 0; success = 0; error = 0
    
    dir = "data/{}".format(date)
    if not os.path.exists(dir):
        os.makedirs(dir)
    name = "/home/pi/mcnex_v2/{}/{}.txt".format(dir, time)
    f = open(name,'a+')
    if os.stat(name).st_size == 0:
        f.write("Total camera tested: {}\n".format(total))
        f.write("Number camera success: {}\n".format(success))
        f.write("Total camera error: {}\n".format(error))
    else:
        f.seek(0)
        total = int(f.readline()[:-1].split(' ')[-1])
        success = int(f.readline()[:-1].split(' ')[-1])
        error = int(f.readline()[:-1].split(' ')[-1])
    f.close()
    return [total, success, error]

def write_data_to_file(date, time, data):
    file_name = "/home/pi/mcnex_v2/data/{}/{}.txt".format(date, time)
    f = open(file_name, 'a+')
    f.seek(0)
    f.write("Total camera tested: {}\n".format(data[0]))
    f.write("Number camera success: {}\n".format(data[1]))
    f.write("Total camera error: {}\n".format(data[2]))
    f.close()

def save_current_time(date, time):
    f = open("/home/pi/mcnex_v2/current_time.txt", 'w+')
    f.write("{} {}".format(date, time))
    f.close()

def get_current_time():
    f = open("/home/pi/mcnex_v2/current_time.txt", 'r')
    date_time =  list(map(int, f.readline().split()))
    f.close()
    return date_time

# if __name__ == "__main__":
    