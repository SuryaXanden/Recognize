import re, json

with open('StatementCsv.csv', mode='r', encoding='UTF-8', errors='strict', buffering=1) as f:
    file_data = f.readlines()

with open('exclude.json') as f:
    omit = json.load(f)

formatted_string = list()

for line in file_data:
    # remove anything within brackets
    line = re.sub("\s?(\(.*\)|(\{.*\})|(\<.*\>)|(\[.*\]))\s?", ' ', line, 0, re.MULTILINE)
    # remove weird symbols
    line = re.sub("[^ \w+\s?]", ' ', line, 0, re.MULTILINE)
    # keep only alphabets and spaces
    line = re.sub("[^\sa-zA-Z]", '', line, 0, re.MULTILINE)
    # lowercase
    line = line.lower()
    # remove multiple spaces
    line = re.sub("\s\s*", ' ', line, 0, re.MULTILINE)
    
    for ex in omit['exclude']:
        line = re.sub(str(ex[0]), str(ex[1]), line, 0, re.MULTILINE)

    # remove multiple spaces
    line = re.sub("\s\s+", ' ', line, 0, re.MULTILINE)
    # remove spaces from beginning and ending of the string
    line = line.strip()

    formatted_string.append(line)

# remove reduncdancy
formatted_string = list(set(formatted_string))
# sort alphabetically
formatted_string = sorted(formatted_string) # comment later

with open('cleaned_file.csv', mode='w', encoding='UTF-8', errors='strict', buffering=1) as f:
    for i in formatted_string:
        f.write(i + '\n')