SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "game.schema.json",
    "title": "Game",
    "description": "Информация об игре",
    "type": "object",
    "required": ["title", "points", "finish"],
    "properties": {
        "title": {"description": "Название игры",
                  "$ref": "#/$defs/title"},
        "slug": {"description": "Название папки игры",
                 "$ref": "#/$defs/slug"},
        "points": {"description": "Точки игры",
                   "type": "array",
                   "items": {"$ref": "#/$defs/point"},
                   "minItems": 1
                   },
        "finish": {"description": "Финальная локация",
                   "type": "object",
                   "required": ["text", "link"],
                   "properties": {
                       "text": {"description": "Сообщение об окончании игры",
                                "type": "string",
                                "minLength": 1
                                },
                       "link": {"$ref": "#/$defs/linkPath"}
                   },
                   "additionalProperties": False
                   }
    },
    "additionalProperties": False,
    "$defs": {
        "point": {
            "type": "object",
            "required": ["title", "location", "task", "answer", "clues", "after_solved"],
            "properties": {
                "title": {"description": "Название точки",
                          "$ref": "#/$defs/title"},
                "location": {"description": "Локация точки",
                             "type": "object",
                             "required": ["link"],
                             "properties": {
                                 "text": {"description": "Описание локации",
                                          "type": "string",
                                          "minLength": 1
                                          },
                                 "link": {"$ref": "#/$defs/linkPath"},
                                 "audio": {"$ref": "#/$defs/audioPath"},
                                 "image": {"$ref": "#/$defs/imagePath"}
                             },
                             "additionalProperties": False
                             },
                "task": {"description": "Задание точки",
                         "type": "object",
                         "required": ["text"],
                         "properties": {
                             "text": {"description": "Текст задания",
                                      "type": "string",
                                      "minLength": 1},
                             "audio": {"$ref": "#/$defs/audioPath"},
                             "image": {"$ref": "#/$defs/imagePath"}
                         },
                         "additionalProperties": False
                         },
                "answer": {"description": "Правильный ответ",
                           "type": "object",
                           "required": ["type", "text"],
                           "properties": {
                               "type": {"description": "Тип ответа",
                                        "type": "string",
                                        "enum": ["text", "photo"]
                                        },
                               "text": {"description": "Правильный ответ или описание того, что должно быть на фото.",
                                        "type": "string",
                                        "minLength": 1}
                           },
                           "additionalProperties": False
                           },
                "clues": {"description": "Подсказки",
                          "type": "array",
                          "items": {
                              "type": "string",
                              "minLength": 1},
                          "minItems": 3,
                          "maxItems": 3
                          },
                "after_solved": {"description": "Реакция на правильный ответ",
                                 "type": "object",
                                 "required": ["text"],
                                 "properties": {
                                     "text": {"description": "Сообщение после правильного ответа",
                                              "type": "string",
                                              "minLength": 1},
                                     "audio": {"$ref": "#/$defs/audioPath"},
                                     "image": {"$ref": "#/$defs/imagePath"}
                                 },
                                 "additionalProperties": False
                                 }
            },
            "additionalProperties": False
        },
        "title": {
            "type": "string",
            "minLength": 1
        },
        "slug": {
            "type": "string",
            "minLength": 1
        },
        "audioPath": {
            "type": "string",
            "pattern": r"^media/audio/.+\.(mp3|wav|ogg)$",
            "minLength": 1
        },
        "imagePath": {
            "type": "string",
            "pattern": r"^media/images/.+\.(jpg|jpeg|png|webp)$",
            "minLength": 1
        },
        "linkPath": {
            "type": "string",
            "anyOf": [
                {"pattern": "^https://(www\\.)?google\\.[a-z.]+/maps/.+"},
                {"pattern": "^https://maps\\.google\\.[a-z.]+/\\?q=.+"},
                {"pattern": "^https://(yandex|maps\\.yandex)\\.[a-z.]+/maps/.+"},
                {"pattern": "^https://(www\\.)?openstreetmap\\.org/.+"},
                {"pattern": "^https://www\\.bing\\.com/maps/.+"},
                {"pattern": "^https://t\\.me/addlocation/.+"}
            ],
            "minLength": 1
        }
    }
}
