import json

with open('/home/hyun/Desktop/Lab/deap/examples/gp/sample.json','r') as json_file:
    json_data=json.load(json_file)

print(json_data['expr']['left'])