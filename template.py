import requests
import json
endpoint = "https://api.veed.io/projects/cb23c1c4-57b8-4746-bdf6-2deb9de943bf"
headers = {
    "Authorization": "[INSERT KEY]",
    "Content-Type": "application/json"
}

project_json = requests.get(endpoint, headers=headers).json()

subtitles = {}
subtitles_key = ""
for k, v in project_json["data"]["edit"]["subtitles"]["tracks"].items():
    if isinstance(v, dict):
        subtitles = v
        subtitles_key = k

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

project_json = requests.put(endpoint, data=json.dumps(project_json), headers=headers).json()


