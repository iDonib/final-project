import csv


def write_voted_to_file(secret):
    if voted(secret):
        return False
    with open('voted.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow([secret])
    print(voted(secret))
    return True

def voted(secret):
    data = []
    f = open('voted.csv')
    reader = csv.reader(f)
    for row in reader:
        data.append(row[0])
    if secret in data:
        return True
    return False
