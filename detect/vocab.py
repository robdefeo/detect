__author__ = 'robdefeo'
import logging

alias_data = None


class Vocab(object):
    def __init__(self, container=None):
        self.container = container
        self.LOGGER = logging.getLogger(__name__)

    def create_container(self):
        from detect.container import Container
        self.container = Container()

    def get_from_database(self):
        if self.container is None:
            self.create_container()

        self.LOGGER.warn("loading data")
        return self.container.data_attribute.find_for_detection(
            [
                "color", "brand", "material", "theme", "style", "detail", "season", "lob", "division"
            ]
        )

    def generate_empty_structure(self, languages):
        new_alias_data = {}
        for x in languages:
            new_alias_data[x] = {}

        return new_alias_data

    def create_values(self, value_type, key, display_name, source, match_type, related):
        redirects = [
            {
                "type": x["attribute"]["type"],
                "key": x["attribute"]["key"],
                "display_name": "display_name",
                "source": source,
                "match_type": match_type
            } for x in related if x["action"] == "redirect"] if related is not None else None
        if redirects is None or not any(redirects):
            return [
                {
                    "type": value_type,
                    "key": key,
                    "display_name": display_name,
                    "source": source,
                    "match_type": match_type
                }
            ]
        else:
            return redirects

    def add_value(self, data, language, key, values):
        if key in data[language]:
            for x in values:
                current_values = ["%s_%s" % (y["type"], y["key"]) for y in data[language][key]]
                if "%s_%s" % (x["type"], x["key"]) not in current_values:
                    data[language][key].append(x)
                    # self.LOGGER.warning(
                    #     "multiple_ids,alias=%s,value=%s",
                    #     key,
                    #     data[language][key]
                    # )

        else:
            data[language][key] = values

    def add_hearts(self, data):
        self.add_value(
            data,
            "en",
            "hearts",
            self.create_values(
                "interest",
                "heart",
                "heart",
                "context",
                "alias",
                None
            )
        )

    def load(self, languages):
        attribute_data = self.get_from_database()
        new_alias_data = self.generate_empty_structure(languages)

        for attribute in attribute_data:
            self.LOGGER.info("processing_atttribute,_id=%s", attribute["_id"])
            for language in languages:
                # loop aliaes
                for alias_attribute in (x for x in attribute["aliases"] if x["language"] == language):
                    self.add_value(
                        new_alias_data,
                        language,
                        alias_attribute["value"],
                        self.create_values(
                            attribute["_id"]["type"],
                            attribute["_id"]["key"],
                            attribute["display_name"] if "display_name" in attribute and attribute["display_name"] else
                            attribute["_id"]["key"],
                            "content",
                            "alias" if "type" not in alias_attribute else alias_attribute["type"],
                            attribute["related"] if "related" in attribute else None
                        )
                    )

        self.add_value(
            new_alias_data,
            "en",
            "popular",
            self.create_values(
                "non_attribute",
                "popular",
                "popular",
                "manual",
                "alias",
                None
            )
        )

        global alias_data
        self.add_hearts(
            new_alias_data
        )
        alias_data = new_alias_data
        return new_alias_data
