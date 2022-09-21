import json

with open("./test_files/performance.json") as file:
    aa=json.loads(file.read())

    for key,value in aa.items():
        print(key+" : "+str(sum(value)/len(value)))
        print(key+" : "+str(sum(value)))

    print()


