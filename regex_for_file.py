import re, json

with open('StatementCsv.csv') as f:
    file_data = f.readlines()

with open('exclude.json') as f:
    omit = json.load(f)

for line in file_data:
    # remove anything within brackets
    line = re.sub("\s?(\(.*\)|(\{.*\})|(\<.*\>)|(\[.*\]))\s?", ' ', line, 0, re.MULTILINE)
    # remove weird symbols
    line = re.sub("[^ \w+\s?]", ' ', line, 0, re.MULTILINE)
    # keep only alphabets and spaces
    line = re.sub("[^\sa-zA-Z]", '', line, 0, re.MULTILINE)
    # lowercase
    line = line.lower()
    
    for ex in omit['exclude']:
        # # # print("Line [{}] will be checked for [{}] and replaced with [{}]".format(line, ex[0], ex[1]))
        line = re.sub(str(ex[0]), str(ex[1]), line, 0, re.MULTILINE)

    # remove multiple spaces
    line = re.sub("\s\s+", ' ', line, 0, re.MULTILINE)
    # remove spaces from beginning and ending of the string
    line = line.strip()


    print(line)

    # with open('op.csv', 'a') as f:
    # # print(line)
# print(omit['internal'][2][0])
  