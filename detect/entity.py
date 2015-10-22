__author__ = 'robdefeo'


class EntityFactory:
    def __init__(self, alias_data):
        self.alias_data = alias_data

    @staticmethod
    def type_match_score(_type_a, _type_b, multiple_key_matches):
        if _type_a == _type_b:
            return 1
        elif len({"lob", "division", "style"}.intersection([_type_a, _type_b])) == 2:
            return 0.999
        elif len({"lob", "division", "theme"}.intersection([_type_a, _type_b])) == 2:
            return 0.990
        elif len({"style", "theme"}.intersection([_type_a, _type_b])) == 2:
            return 0.999
        elif multiple_key_matches:
            return 0.8
        else:
            return 0.9

    def create(self, _type, key, suggested=None, source=None, confidence=99.99999):
        disambiguated_outcomes = []
        if key in self.alias_data["en"]:
            for x in self.alias_data["en"][key]:
                # TODO can suggest flag be used for somehthing not sure

                confidence *= self.type_match_score(x["type"], _type, len(self.alias_data["en"][key]) > 1)

                if x["match_type"] == "alias":
                    confidence *= 1
                elif x["match_type"] == "spelling":
                    confidence *= 0.9

                disambiguated_outcomes.append(
                    {
                        "key": x["key"],
                        "type": x["type"],
                        "source": source if source is not None else x["source"],
                        "display_name": x["display_name"],
                        "confidence": confidence
                    }
                )

        else:
            pass

        if not any(x for x in disambiguated_outcomes if x["key"] == key and x["type"] == _type):
            disambiguated_outcomes.append(
                {
                    "key": key,
                    "type": _type,
                    "source": "unknown",
                    "display_name": key,
                    "confidence": 20.0
                }
            )

        sorted_disambiguations = sorted(disambiguated_outcomes, key=lambda y: y["confidence"], reverse=True)

        ret = {
            "confidence": sorted_disambiguations[0]["confidence"],
            "key": sorted_disambiguations[0]["key"],
            "type": sorted_disambiguations[0]["type"],
            "source": sorted_disambiguations[0]["source"],
            "display_name": sorted_disambiguations[0]["display_name"]
        }

        if len(sorted_disambiguations) > 1:
            ret["disambiguate"] = sorted_disambiguations[1:]

        return ret
