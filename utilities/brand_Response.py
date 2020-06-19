import json

class BrandResponse:
    '''This is BrandResponse class'''
    
    def __init__(self, brand_name, count_data):
        self.brand_name = brand_name
        self.count_data = count_data
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)