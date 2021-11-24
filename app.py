from flask import Flask, request
from urllib.parse import urlencode
import os
import hmac
import time
import hashlib
import requests
import json
import re
import pandas

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    if valid_request():
        response = veed_templating()
        if response is None:
            return "Processed " + request.form["text"] + " - Refresh the page to see changes."
        else:
            return response
    return "Permissions validation failed"

@app.route('/copy', methods=['POST'])
def veed_copy():
    if valid_request():
        response = veed_copy()
        if response is None:
            return "Copied: " + request.form["text"] + " View: https://www.veed.io/workspaces/772f58ea-eaf2-4036-897a-922298b1b92f/projects"
        else:
            return response
    return "Permissions validation failed"

@app.route('/generate', methods=['POST'])
def veed_generate():
    if valid_request():
        response = generate_from_sheet()
        return "New video started: " + response
    return "Permissions validation failed"

def valid_request():
    timestamp = request.headers['X-Slack-Request-Timestamp']
    if abs(time.time() - int(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return
    slack_signing_secret = os.environ['slack_signing_secret'].encode('utf-8')
    request_body = request.form
    sig_basestring = 'v0:' + timestamp + ':' + urlencode(request_body)
    sig_basestring = sig_basestring.encode('utf-8')
    my_signature = 'v0=' + hmac.new(slack_signing_secret, sig_basestring, hashlib.sha256).hexdigest()
    slack_signature = request.headers['X-Slack-Signature']

    if my_signature == slack_signature:
        return True
    return False

def veed_templating():
    project_id = re.search("[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}", request.form["text"])
    if project_id is None:
        return "Invalid project provided. Please use the project's link."
    endpoint = "https://api.veed.io/projects/" + project_id.group()
    headers = {
        "Authorization": os.environ['token'],
        "Content-Type": "application/json"
    }

    project_json = requests.get(endpoint, headers=headers).json()
    subtitles = {}
    for k, v in project_json["data"]["edit"]["subtitles"]["tracks"].items():
        if isinstance(v, dict):
            subtitles = v

    audio_end = 0
    for v in project_json["data"]["edit"]["audioStreams"].values():
        audio_end = max(audio_end, v["trimEnd"])
    intro = { "start": 0, "end": 0}
    intro_value = ""
    closing = { "start": 0, "end": audio_end}
    last_subtitle_end = 0
    last_subtitle_key = ""
    for k, v in subtitles["items"].items():
        if v["from"] == 0:
            intro["end"] = v["to"]
            intro_value = v["words"]
        if v["to"] > last_subtitle_end:
            closing["start"] = v["from"]
            last_subtitle_end = v["to"]
            last_subtitle_key = k

    subtitles["items"][last_subtitle_key]["words"] = intro_value
    subtitles["items"][last_subtitle_key]["to"] = audio_end

    text_properties = {
        "value": "Cantonese Terms ",
        "font": "Roboto",
        "size": 0.036,
        "display": "line_block_round",
        "color": "#FECB2FFF",
        "align": "center",
        "emphasis": "bold",
        "rotation": 0,
        "from": 0,
        "to": audio_end,
        "textWrap": "wrap",
        "wrapWidth": 1,
        "lineHeight": 1,
        "letterSpacing": 0,
        "zIndex": 4,
        "x": 0.5,
        "y": 0.09325079872204473,
        "bg": "#000000FF"
    }

    video_term = ""
    video_term_end = 1000000000
    for k, v in project_json["data"]["edit"]["text"].items():
        if v["to"] < video_term_end:
            video_term_end = v["to"]
            video_term = v["value"]

    project_json["data"]["edit"]["text"] = {}
    project_json["data"]["edit"]["text"]["cantoneseTerms"] = text_properties.copy()

    text_properties["value"] = "@BLMCantonese"
    text_properties["y"] = 0.9339218659734257
    text_properties["zIndex"] = 0
    project_json["data"]["edit"]["text"]["@blmcantonese"] = text_properties.copy()

    text_properties["value"] = "Example:"
    text_properties["size"] = 0.048
    text_properties["display"] = "normal"
    text_properties["color"] = "#000000"
    text_properties["emphasis"] = "normal"
    text_properties["from"] = intro["end"]
    text_properties["to"] = closing["start"]
    text_properties["zIndex"] = 1
    text_properties["bg"] = "#ffffff"
    text_properties["y"] = 0.17233181588265042
    project_json["data"]["edit"]["text"]["example"] = text_properties.copy()

    text_properties["value"] = video_term
    text_properties["size"] = 0.06
    text_properties["display"] = "normal"
    text_properties["color"] = "#000000"
    text_properties["emphasis"] = "bold"
    text_properties["from"] = 0
    text_properties["to"] = intro["end"]
    text_properties["zIndex"] = 2
    text_properties["bg"] = "#ffffff"
    text_properties["y"] = 0.2791666666666667
    project_json["data"]["edit"]["text"]["termOpen"] = text_properties.copy()

    text_properties["from"] = closing["start"]
    text_properties["to"] = audio_end
    text_properties["zIndex"] = 3
    project_json["data"]["edit"]["text"]["termClose"] = text_properties.copy()

    response = requests.put(endpoint, data=json.dumps(project_json), headers=headers);
    project_json = response.json()
    return None


def veed_copy():
    project_id = re.search("[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}", request.form["text"])
    if project_id is None:
        return "Invalid project provided. Please use the project's link."
    endpoint = "https://api.veed.io/projects/" + project_id.group()
    headers = {
        "Authorization": os.environ['token'],
        "Content-Type": "application/json"
    }

    project_json = requests.get(endpoint, headers=headers).json()

    endpoint = "https://api.veed.io/projects/workspaces/772f58ea-eaf2-4036-897a-922298b1b92f"
    json_copy = {
        "duplicatedFrom": project_id.group(),
        "folder": "/"
    }
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
    project_json = requests.post(endpoint, data=json.dumps(json_copy), headers=headers).json()

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
    project_json = requests.post(endpoint, data=json.dumps(json_copy), headers=headers).json()

    return None


def generate_from_sheet():
    link = os.environ['googlesheet']
    df = pandas.read_csv(link, header=1)
    sheet_data = df.iloc[int(request.form["text"])-3][['English', 'Cantonese', 'Example (English)', 'Example (Cantonese)', 'Cantonese romanization']]
    
    token = os.environ['token']
    template_id = "5712ea1d-9815-4560-b015-4dbf3ba6eda1"
    endpoint = "https://api.veed.io/projects/" + template_id
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    template_json = requests.get(endpoint, headers=headers).json()
    for k, v in template_json["data"]["edit"]["text"].items():
        if v["value"] == "[INSERT TERM]":
            template_json["data"]["edit"]["text"][k]["value"] = sheet_data["English"].capitalize()

    example_subtitle = sheet_data["Example (English)"] + "\n⎼⎼⎼⎼⎼\n" + sheet_data["Example (Cantonese)"] + "\n" + sheet_data["Cantonese romanization"]
    
    new_subtitles = [sheet_data["Cantonese"], example_subtitle, sheet_data["Cantonese"]]
    for k, v in template_json["data"]["edit"]["subtitles"]["tracks"].items():
        if isinstance(v, dict):
            subtitles = v
            subtitle_key = k
    for k,v in subtitles["items"].items():
        if len(new_subtitles) > 0:
            new_value = new_subtitles.pop(0)
            subtitles["items"][k]["words"] =  [
                {
                    "value": new_value,
                    "from": None,
                    "to": None,
                    "confidence": None
                }
            ]
    template_json["data"]["edit"]["subtitles"]["tracks"][subtitle_key] = subtitles

    new_project = {
        "duplicatedFrom": template_id,
        "folder": "/",
        "name": sheet_data["English"].capitalize() + " - IG"
    }
    new_project["data"] = template_json["data"]
    endpoint = "https://api.veed.io/projects/workspaces/772f58ea-eaf2-4036-897a-922298b1b92f"
    new_json = requests.post(endpoint, data=json.dumps(new_project), headers=headers).json()
    return "https://www.veed.io/edit/" + new_json["id"]


    
    