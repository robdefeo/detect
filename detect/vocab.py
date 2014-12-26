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

    def generate(self):
        if self.container is None:
            self.create_container()

        self.LOGGER.warn("generating data")
        self.container.data_attribute.map_reduce_aliases(
            [
                "color", "brand", "material", "theme", "style"
            ]
        )

    def load(self):
        if self.container is None:
            self.create_container()

        self.LOGGER.warn("loading data")
        raw_data = self.container.data_attribute_alias.find_all()
        new_alias_data = {
            "en": {}
        }
        for x in raw_data:
            if len(x["value"]["_ids"]) != 1:
                self.LOGGER.warning(
                    "multiple_ids,alias=%s",
                    x["_id"]
                )

            if x["_id"]["language"] in ["en"]:
                new_alias_data["en"][x["_id"]["value"]] = x["value"]["_ids"][0]

        global alias_data
        alias_data = new_alias_data
        new_alias_data["en"]["hearts"] = {
            u'type': u'interest', u'key': u'heart'
        }
        return new_alias_data