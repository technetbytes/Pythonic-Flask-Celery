import json

class CategoryResponse:
    '''This is CategoryResponse class'''
    
    def __init__(self, category_Name, subcategory_name, subcategory_data, view_type ="Bar"):
        self.category_Name = category_Name
        self.view_type = view_type
        self.subcategory_name = subcategory_name
        self.subcategory_data = subcategory_data

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)