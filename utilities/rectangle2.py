from utilities.point import Point
class Rectangle2(object):
    
    def __init__(self, bottom_left_x=0.0, bottom_left_y=0.0, init_width=0.0, init_height=0.0):
        self.bottom_left = Point(bottom_left_x, bottom_left_y)
        self.width = init_width
        self.height = init_height