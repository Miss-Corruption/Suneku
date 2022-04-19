import json
import re


async def _parse_details(entries):
    lengths = {
        1: "Very short (<2 hours)",
        2: "Short (2 - 10 hours)",
        3: "Medium (10 - 30 hours)",
        4: "Long (30 - 50 hours)",
        5: "Very long (> 50 hours)"
    }
    regex = r"\[url=((?:http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+(?:[\-\.]{1}[a-z0-9]+)*" \
            r"\.[a-z]{2,5}(?:[0-9]{1,5})?(?:\/[^\]]+))\]([^\[]+)\[/url\]"
    reg_compiled = re.compile(regex, re.IGNORECASE)
    description = "n/A"
    aliases_str = str(entries.get('aliases', "")).replace("\n", ", ")
    aliases_stripped = [x.strip() for x in aliases_str.split(',')]
    length = lengths.get(entries['length'], 'n/A')
    if entries["description"]:
        description = reg_compiled.sub("[\\2](\\1)", entries["description"], 0)
    return aliases_stripped, length, description


async def _parse_relations(entries):
    if entries["relations"]:
        related_dict = {}
        for related_vn in entries["relations"]:
            related_dict[related_vn["original"]] = {
                "ID": related_vn["id"],
                "Title": related_vn["title"],
                "Relation": related_vn["relation"],
                "Is Official?": related_vn["official"]
            }
        return related_dict
    else:
        return None


async def _parse_anime(entries):
    if entries["anime"]:
        anime_dict = {}
        for anime in entries["anime"]:
            anime_dict[anime["title_romaji"]] = {
                "anidb_id": anime["id"],
                "ann_id": anime["ann_id"],
                "nfo_id": anime["nfo_id"],
                "title_kanji": anime["title_kanji"],
                "type": anime["type"]
            }
        return anime_dict
    else:
        return None


async def _parse_screens(entries):
    if entries["screens"]:
        screen_dict = {}
        for screen in entries["screens"]:
            screen_dict[screen["rid"]] = {
                "url": screen["image"],
                "nsfw": screen["nsfw"],
                "flagging": {
                    "violence": screen["flagging"]["violence_avg"],
                    "sexuality": screen["flagging"]["sexual_avg"],
                    "votecount": screen["flagging"]["votecount"]
                },
                "width": screen["width"],
                "height": screen["height"]
            }
        return screen_dict
    else:
        return None


async def _parse_staff(entries):
    if entries["staff"]:
        staff_dict = {}
        for staff in entries["staff"]:
            staff_dict[staff["sid"]] = {
                "aid": staff["aid"],
                "name": staff["name"],
                "original": staff["original"],
                "role": staff["role"],
                "note": staff["note"]
            }
        return staff_dict
    else:
        return None


async def humanize_vn(data):
    hmn_data = {}
    temp = json.dumps(data[1]["items"], indent=2)
    print(temp)
    for entries in data[1]["items"]:
        alias, length, description = await _parse_details(entries)
        relations = await _parse_relations(entries)
        anime = await _parse_anime(entries)
        screens = await _parse_screens(entries)
        staff = await _parse_staff(entries)
        hmn_data[entries["id"]] = {
            "basic": {
                "title": entries["title"],
                "original": entries["original"],
                "released": entries["released"],
                "languages": entries["languages"],
                "orig_lang": entries["orig_lang"],
                "platforms": entries["platforms"]
            },
            "details": {
                "aliases": alias,
                "length": length,
                "description": description,
                "links": {
                    "encubed": entries["links"]["encubed"],
                    "wikipedia": entries["links"]["wikipedia"],
                    "renai": entries["links"]["renai"],
                    "wikidata": entries["links"]["wikidata"],
                },
                "image": {
                    "url": entries["image"],
                    "nsfw": entries["image_flagging"],
                    "flagging": {
                        "violence": entries["image_flagging"]["violence_avg"],
                        "sexuality": entries["image_flagging"]["sexual_avg"]
                    }
                }
            },
            "anime": anime,
            "relations": relations,
            "tags": None,
            "stats": {
                "popularity": entries["popularity"],
                "rating": entries["rating"],
                "votecount": entries["votecount"]
            },
            "screens": screens,
            "staff": staff
        }
    with open("Output.json", "w+") as jsonFile:
        json.dump(hmn_data, jsonFile, indent=4)
        jsonFile.truncate()
