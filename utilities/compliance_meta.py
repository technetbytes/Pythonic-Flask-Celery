import json

class ComplianceMetaData(object):

    def __init__(self, shelf_items, match_compliance_items, shelf_name=None, shelf_tag=None, compliance_items_count=0.0, shelf_items_count=0.0, ratio=0.0, compliance_level=0.0):
        self.shelf_name = shelf_name
        self.shelf_tag = shelf_tag
        self.shelf_items = shelf_items
        self.match_compliance_items = match_compliance_items
        self.total_compliance_items_count = compliance_items_count
        self.total_shelf_items_count = shelf_items_count
        self.ratio = ratio
        self.compliance_level = compliance_level

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
