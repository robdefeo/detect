Basically get close to this https://wit.ai/docs/intro but better suited

#Response
Current version

{

    "timestamp": "2015-03-17T16:23:14.706937",
    "detection_id": "550846e2bf5f60449d35a396",
    "detections": [
        {
            "type": "style",
            "key": "heels",
            "source": "content"
        },
        {
            "type": "color",
            "key": "orange",
            "source": "content"
        },
        {
            "type": "color",
            "key": "blue",
            "source": "content"
        },
        {
            "type": "style",
            "key": "high heels",
            "source": "content"
        },
        {
            "type": "material",
            "key": "fur",
            "source": "content"
        }
    ],
    "autocorrected_query": "white and blue high heels with fur and orange",
    "non_detections": [ ],
    "version": "1.0.0"
}

Proposed
{

    "timestamp": "2015-03-17T16:23:14.706937",
    "detection_id": "550846e2bf5f60449d35a396",
    "intents": [
        {
            "type": "include",
            "entities":[
                {
                    "type": "style",
                    "key": "heels",
                    "source": "content"
                },
                {
                    "type": "color",
                    "key": "orange",
                    "source": "content"
                },
                {
                    "type": "color",
                    "key": "blue",
                    "source": "content"
                },
                {
                    "type": "style",
                    "key": "high heels",
                    "source": "content"
                },
                {
                    "type": "material",
                    "key": "fur",
                    "source": "content"
                }
            ]
        }
    ],
    "autocorrected_query": "white and blue high heels with fur and orange",
    "non_detections": [ ],
    "version": "1.0.0"
}