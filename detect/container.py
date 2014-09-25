__author__ = 'robdefeo'


class Container(object):
    def __init__(self):
        from prproc.data.attribute import Attribute
        self.data_attribute = Attribute()
        self.data_attribute.open_connection()

        from prproc.data.alias_attribute import AliasAttribute
        self.data_attribute_alias = AliasAttribute()
        self.data_attribute_alias.open_connection()