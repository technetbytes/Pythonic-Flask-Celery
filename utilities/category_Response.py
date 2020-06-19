import json

class CategoryResponse:
    '''This is CategoryResponse class'''
    
    def __init__(self, categoryName, subcategory_name, subcategory_data):
        self.categoryName = categoryName
        self.subcategory_name = subcategory_name
        self.subcategory_data = subcategory_data

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)