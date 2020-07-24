class CategoryDetail:
    '''This is CategoryDetail class'''
    
    def __init__(self,category_id, category_name, dataContainer, category_description, show_type, subcategory_id, subcategory_name, tages):
        self.category_id = category_id
        self.category_name = category_name
        self.show_type = show_type
        self.dataContainer = dataContainer
        self.category_description = category_description
        self.subcategory_id = subcategory_id
        self.subcategory_name = subcategory_name
        self.tages = tages