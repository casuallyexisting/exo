import csv

imsg_files = ['mac_log.csv','hja_log.csv','br_log.csv','cbc_log.csv','sklog.csv','zm_log.csv']
discord_files = []

def parse_imsg_csv(files):
    #holds all usernames for simulating conversation later
    usernames = []
    input_filenames = files
    #the code will append 'Train.txt' and 'Test.txt' for you
    output_filename = "output/parsed_"
    for file in input_filenames:
        #count number of lines
        total = None
        with open(file, encoding='utf-8') as f:
            total = sum(1 for line in f)


        counter = 0
        with open(file, newline = '', encoding='utf-8') as infile:
            inreader =  csv.reader(infile, delimiter=',')#, quotechar = '', quoting=csv.QUOTE_ALL)

            with open(output_filename + 'Train.txt', 'a+', encoding='utf-8') as trainfile:
                with open(output_filename + 'Test.txt', 'a+', encoding='utf-8') as testfile:
                    for l in inreader:
                        print(l)
                        if l[2] == "":
                            continue
                        if l[0] not in usernames:
                            usernames.append(l[0])
                        if counter < float(total)*.95:
                            trainfile.write(l[0] + ": " + l[2] + "\n")
                        else:
                            testfile.write(l[0] + ": " + l[2] + "\n")
                        counter += 1
        #holds usernames for simulating conversation
        with open(output_filename+'Usernames.txt', 'a+') as usersfile:
            for name in usernames:
                usersfile.write(name + "\n")

def parse_dm_csv(files):
    #holds all usernames for simulating conversation later
    usernames = []
    input_filename = files
    #the code will append 'Train.txt' and 'Test.txt' for you
    output_filename = "output/parsed_"

    for file in files:
        #count number of lines
        total = None
        with open(file, encoding='utf-8') as f:
            total = sum(1 for line in f)


        counter = 0
        with open(file, newline = '', encoding='utf-8') as infile:
            inreader =  csv.reader(infile, quotechar = '"', delimiter=',', quoting=csv.QUOTE_ALL)

            with open(output_filename + 'Train.txt', 'a+', encoding='utf-8') as trainfile:
                with open(output_filename + 'Test.txt', 'a+', encoding='utf-8') as testfile:
                    for l in inreader:
                        print(l)
                        if l[3] == "":
                            continue
                        if l[1][:-5] not in usernames:
                            usernames.append(l[1][:-5])
                        if counter < float(total)*.95:
                            trainfile.write(l[1][:-5] + ": " + l[3] + "\n")
                        else:
                            testfile.write(l[1][:-5] + ": " + l[3] + "\n")
                        counter += 1
        #holds usernames for simulating conversation
        with open(output_filename+'Usernames.txt', 'a+') as usersfile:
            for name in usernames:
                usersfile.write(name + "\n")

parse_imsg_csv(imsg_files)
parse_dm_csv(discord_files)
