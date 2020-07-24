from utilities.rectangle import Rectangle
from utilities.point import Point
import math

def rectangle_contain(self, r1=Rectangle(), r2=Rectangle()):
    v = (r1.x <= r2.x) and (r1.y <= r2.y) and (r1.x + r1.w >= r2.x + r2.w) and (r1.y + r1.h >= r2.y + r2.h) and (r1.x + r1.w > r2.x) and (r1.y + r1.h > r2.y)
    return v

def is_point_within_dist_of_rect(rect=Rectangle(), point=Point(), dist=0.0):    
    if((rect.bottom_left.x - dist)< point.x and point.x < (rect.bottom_left.x + rect.width + dist)):        
        if(point.x < rect.bottom_left.x):                
            a = rect.bottom_left.x - point.x
            y_max = rect.bottom_left.y + rect.height + math.sqrt(dist**2-a**2)
            y_min = rect.bottom_left.y - math.sqrt(dist**2-a**2)
                
            if((y_min < point.y) and point.y < y_max):
                return True
            else:
                return False
                
        elif(point.x < (rect.bottom_left.x + rect.width)):
                
            y_max = rect.bottom_left.y + rect.height + dist
            y_min = rect.bottom_left.y - dist
                
            if((y_min < point.y) and point.y < y_max):
                return True
            else:
                return False
                
        else:

            a = rect.bottom_left.x+rect.width - point.x
            y_max = rect.bottom_left.y + rect.height + math.sqrt(dist**2-a**2)
            y_min = rect.bottom_left.y - math.sqrt(dist**2-a**2)
                
            if((y_min < point.y) and point.y < y_max):
                return True
            else:
                return False
        
    return False

