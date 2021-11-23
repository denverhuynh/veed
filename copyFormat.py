import requests
import json
endpoint = "https://api.veed.io/projects/8e6b5b33-0420-4547-8e5a-a8f51e337ebb"
headers = {
    "Authorization": "[INSERT KEY]",
    "Content-Type": "application/json"
}

project_json = requests.get(endpoint, headers=headers).json()

endpoint = "https://api.veed.io/projects/workspaces/772f58ea-eaf2-4036-897a-922298b1b92f"
new_json = requests.post(endpoint, headers=headers).json()
id = new_json.pop("id")

json_copy = {}
json_copy["name"] = project_json["name"].split("-")[0] + "- Youtube"
json_copy["data"] = project_json["data"]
json_copy["data"]["edit"]["aspect"]["width"] = 16
json_copy["data"]["edit"]["aspect"]["height"] = 9
json_copy["data"]["edit"]["subtitles"]["size"] = 0.030
json_copy["data"]["edit"]["subtitles"]["emphasis"] = "bold"
for k, v in json_copy["data"]["edit"]["text"].items():
    if "Cantonese Terms" in v["value"] or "@BLMCantonese" in v["value"]:
        json_copy["data"]["edit"]["text"][k]["size"] = 0.020
    elif v["value"] == "Example:":
        json_copy["data"]["edit"]["text"][k]["size"] = 0.024
        json_copy["data"]["edit"]["text"][k]["emphasis"] = "bold"
endpoint = "https://api.veed.io/projects/" + id
project_json = requests.put(endpoint, data=json.dumps(json_copy), headers=headers).json()

endpoint = "https://api.veed.io/projects/workspaces/772f58ea-eaf2-4036-897a-922298b1b92f"
new_json = requests.post(endpoint, headers=headers).json()
id = new_json.pop("id")

json_copy["name"] = project_json["name"].split("-")[0] + "- TikTok"
json_copy["data"]["edit"]["aspect"]["width"] = 9
json_copy["data"]["edit"]["aspect"]["height"] = 16
json_copy["data"]["edit"]["subtitles"]["size"] = 0.048
json_copy["data"]["edit"]["subtitles"]["y"] = 0.4497713539388261
for k, v in json_copy["data"]["edit"]["text"].items():
    if "Cantonese Terms" in v["value"] or "@BLMCantonese" in v["value"]:
        json_copy["data"]["edit"]["text"][k]["size"] = 0.036
        json_copy["data"]["edit"]["text"][k]["x"] = 0.5
        json_copy["data"]["edit"]["text"][k]["y"] = 0.09325079872204473 if "Cantonese Terms" in v["value"] else 0.720473031918213

    elif v["value"] == "Example:":
        json_copy["data"]["edit"]["text"][k]["size"] = 0.048
    else:
        json_copy["data"]["edit"]["text"][k]["size"] = 0.096
endpoint = "https://api.veed.io/projects/" + id
project_json = requests.put(endpoint, data=json.dumps(json_copy), headers=headers).json()
