__author__ = 'm2'
import json

a = json.loads('{"example":{"name":"hello","value":"world"},"example2":{"foo":"bar"}}')
print(a["example"])

for i,v in a["example"].items():
    print(i)
    print(v)