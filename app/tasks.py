from app import celery
from celery.utils.log import get_task_logger

from bridge.bridge_manager import BridgeManager
from models.modelDetail import AiModelDetail
from models.receiveJobs import ReceiveJobs
from models.category import Category
from models.subcategory import SubCategory
from models.compliance import ShelfCompliance
from utilities.category_Detail import CategoryDetail
from utilities.category_Response import CategoryResponse
from utilities.brand_Response import BrandResponse
from utilities.complex_encoder import ComplexEncoder
from utilities.rectangle2 import Rectangle2
from utilities.point import Point
from utilities.geometery_operation import is_point_within_dist_of_rect
from utilities.geometery_operation import rectangle_contain
from utilities.compliance_meta import ComplianceMetaData

from utilities.constant import JOB_STATUS_DONE, JOB_STATUS_ERROR, JOB_STATUS_INSERTED, JOB_STATUS_PENDING, JOB_STATUS_COMMUNICATION_ERROR

from utilities.common import get_url
import requests
import json


logger = get_task_logger(__name__)

def build_shelf_compliance(model_response_json, shelf_compliance):    
    # collection of brand with coordinates
    # sample data formate
    # [item_or_brand_name, x, y, h, w]
    
    brand_tags_xy_data = model_response_json["MetaData"]        
    print_debug_detail(f"{brand_tags_xy_data}")
    compliance_collection = []
    shelf_coordinate_object = None
    for each_shelf in shelf_compliance:            
        compliance_items = each_shelf.complianceItem.split(",")
        print_debug_info(f"Shelf Name and Tag:- {each_shelf.shelfName, each_shelf.shelfTag}")
        #get main shelf coordinate detail
        for single_item_coordinate in brand_tags_xy_data:            
            if single_item_coordinate[0] == each_shelf.shelfTag:
                print_debug_info(f"Actual Shelf Name is:- {single_item_coordinate[0]}")
                shelf_coordinate_object = single_item_coordinate
                break
        
        print_debug_detail(f"Shelf object -> {shelf_coordinate_object}")
        if shelf_coordinate_object is not None:

            #creat shelf Rectangle object
            #logger.info(f"{shelf_coordinate_object[2]}  {float(shelf_coordinate_object[2]+10)}")

            shelf_rectangle = Rectangle2(shelf_coordinate_object[1]-1,float(shelf_coordinate_object[2]-1),shelf_coordinate_object[3],shelf_coordinate_object[4])
            
            #logger.info(f"finding shelf rectangle {shelf_rectangle.x,shelf_rectangle.y,shelf_rectangle.w,shelf_rectangle.h}")
            
            find_item_inside_shelf = []
            #using loop searh compliance item in the shelf
            for each_item_coordinate in brand_tags_xy_data:
                predicted_item_name = each_item_coordinate[0]

                print_debug_info(f"Inner item Name:- {predicted_item_name}")

                #creat searchable item Rectangle object
                #find_rectangle = Rectangle(each_item_coordinate[1],each_item_coordinate[2],each_item_coordinate[3],each_item_coordinate[4])                
                #logger.info(f"item object coordinate -> {find_rectangle.x,find_rectangle.y,find_rectangle.w,find_rectangle.h}")

                item_xy_point = Point(each_item_coordinate[1], each_item_coordinate[2])
                print_debug_detail(f"Inner item x,y value {each_item_coordinate[1]}, {each_item_coordinate[2]}")
                
                #perform search
                is_rect_inside = is_point_within_dist_of_rect(shelf_rectangle, item_xy_point, dist=1)                
                print_debug_detail(f"Item found inside:- {is_rect_inside}")
                if is_rect_inside:
                    find_item_inside_shelf.append(predicted_item_name)
            
            print_debug_info(f"Inside item found length: {len(find_item_inside_shelf)}")
            if len(find_item_inside_shelf) > 0:
                #total compliance item formula using intersection of two sets
                comp_list_as_set = set(compliance_items)
                intersection = comp_list_as_set.intersection(find_item_inside_shelf)
                final_intersected_compliance_items = list(intersection)

                print_debug_info(f"compliance items list {final_intersected_compliance_items}")
                
                total_compliance_items_count = len(final_intersected_compliance_items)
                total_shelf_items_count = len(find_item_inside_shelf)
                total_ratio = total_compliance_items_count / total_shelf_items_count
                compliance_metadata = ComplianceMetaData(find_item_inside_shelf,
                final_intersected_compliance_items,
                each_shelf.shelfName,
                each_shelf.shelfTag,
                total_compliance_items_count,
                total_shelf_items_count,
                total_ratio,
                each_shelf.complianceLevel)
                compliance_collection.append(compliance_metadata)
            else:
                logger.info(f"No Compliance item found")

            print_debug_detail(f"loop-end")

        else:
            logger.info(f"Shelf not found")
    print_debug_detail(f"main-loop-end")
    
    json_string = json.dumps([ob.__dict__ for ob in compliance_collection], cls=ComplexEncoder)
    print_debug_detail(f"Compliance Json data")
    print_debug_detail(f"{json_string}")
    print_debug_info(f"exit from build_shelf_compliance")
    return json_string

def build_analytics(category_detail_obj, model_response_json): 
    actual_group_data = None
    actual_group_name = []
    #build analytics information
    category_response = []
    #build topline information
    topline_response = []

    group_data = model_response_json['GroupData']    
    print_debug_info(f"length of group_data is {len(group_data)}")
    for v in group_data:            
        actual_group_data = json.loads(v)            
        for each_key in actual_group_data:
            actual_group_name.append(each_key['BRAND'])
    
    for cat_obj in category_detail_obj:
        tages = cat_obj.tages.split(",")
        not_found_brand = list(set(tages)-set(actual_group_name))
        found_brand = list(set(tages)-set(not_found_brand)) 
       
        temp_tags_counter = []
        for fb in found_brand:
            ag_data_item = next(item for item in actual_group_data if item["BRAND"] == fb)
            temp_tags_counter.append(BrandResponse(ag_data_item['BRAND'], ag_data_item['COUNT']))
        for nfb in not_found_brand:
            temp_tags_counter.append(BrandResponse(nfb,0))

        if cat_obj.dataContainer == "Analytics":
            print_debug_detail(" Is Analytics Type ")
            category_response.append(CategoryResponse(cat_obj.category_name , cat_obj.subcategory_name, temp_tags_counter, cat_obj.show_type))
        else:
            print_debug_detail(" Is TopLine Type ")
            topline_response.append(CategoryResponse(cat_obj.category_name , cat_obj.subcategory_name, temp_tags_counter, cat_obj.show_type))

    json_string = json.dumps([ob.__dict__ for ob in category_response], cls=ComplexEncoder)
    topline_json_string = json.dumps([ob.__dict__ for ob in topline_response], cls=ComplexEncoder)
    
    print_debug_detail(f"Analytic Json data")
    print_debug_detail(f"{json_string}")
    print_debug_detail(f"Topline analytic Json data")
    print_debug_detail(f"{topline_json_string}")
    print_debug_info(f"exit from build_analytics")
    return json_string, topline_json_string

def build_analytics_and_compliance(category_detail_obj, model_response, shelf_compliance):
    # temp for dev or testing
    #response_obj = requests.get("http://knowhow.markematics.net/ReceiveJobs/GetJobDetailById/2")
    #logger.info(response_obj.text)
    # for dev or testing
    #model_response_json = json.loads(response_obj.text)  
    
    # for live
    model_response_json = json.loads(model_response)

    print_debug_detail("model_response json loaded")        
    print_debug_detail(f"{model_response_json}")

    #build analytic json
    print_debug_info("Calling build analytics")            
    analytic_json, topline_json_string = build_analytics(category_detail_obj, model_response_json)
    
    #build compliance json
    print_debug_info("Calling build compliance")
    compliance_json = build_shelf_compliance(model_response_json, shelf_compliance)    

    # here rebuild the json object using [GroupData, UngroupData, BrandName, Compliance, Analytics] objects
    print_debug_info("Compiling Compliance & Analytics Json response")
    json_response = json.dumps({"GroupData":model_response_json['GroupData'],"UngroupData":model_response_json['UngroupData'],"BrandName":model_response_json['BrandName'],"Compliance":compliance_json,"Analytics":analytic_json,"Topline":topline_json_string})
    print_debug_detail(json_response)
    return json_response

def print_debug_info(data):
    is_debug = True
    if is_debug:
        logger.info(data)

def print_debug_detail(data):
    is_debug = True
    if is_debug:
        logger.info(data)

@celery.task()
def process_image(job_id, model_id, project_id):
    model_detail_obj = None
    received_job_obj = None

    category_detail_obj = []

    print_debug_info("process_image_call")
    bridge = BridgeManager().get_Instance().get_Bridge()
    
    print_debug_info("getting_model_detail_call")    
    model_details = bridge.get_db().get_session().query(AiModelDetail).filter(AiModelDetail.modelID == model_id)

    for model in model_details:
        print_debug_info(f"{model.id} {model.port} {model.url} {model.version} {model.modelJson} {model.status} {model.modelID}")
        model_detail_obj = model
    logger.info(model_detail_obj)
    
    print_debug_info("getting_job_detail")
    received_jobs = bridge.get_db().get_session().query(ReceiveJobs).filter(ReceiveJobs.id == job_id)
    for job in received_jobs:
        print_debug_info(f"{job.unProcessedImage} {job.uri}")
        received_job_obj = job
    logger.info(received_job_obj)

    print_debug_info("category_and_subcategory_loading")
    category_obj = bridge.get_db().get_session().query(Category).filter(Category.projectId == project_id)

    print_debug_info("shelf_compliance_loading")
    shelf_compliance_obj = bridge.get_db().get_session().query(ShelfCompliance).filter(ShelfCompliance.projectId == project_id)

    for category in category_obj:
        print_debug_info(f"{category.categoryName}")        
        sub_category_obj = bridge.get_db().get_session().query(SubCategory).filter(SubCategory.categoryId == category.id)   
        for sub_category in sub_category_obj:
            print_debug_info(f"{sub_category.name}")
            category_detail_obj.append(CategoryDetail(category.id, category.categoryName, category.dataContainer, category.categoryDescription, category.showType, sub_category.id, sub_category.name, sub_category.tages))

    # temp dev or testing analytics
    #build_analytics_and_compliance(category_detail_obj,"",shelf_compliance_obj)

    print_debug_info("checking_pending_job_status")
    if received_job_obj != None:
        # Checking received job status
        if received_job_obj.requestStatus.lower() == JOB_STATUS_INSERTED:#len(received_job_obj.requestStatus.lower()) > 0:
            print_debug_info(received_job_obj.requestStatus)
            print_debug_info(f"Updating status value from Inserted to Pending against {job_id}")

            # Update received job status into PENDING            
            bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_PENDING})
            bridge.get_db().get_session().commit()
            
            # Generating image processing request url
            request_url = get_url(model_detail_obj.url, model_detail_obj.port, "upload-image")

            print_debug_info(f"Generating image processing request url {request_url}")
            try:
                # Sending image to model for analysis
                headers = {'Content-type': 'application/json'}
                request_data = {'data_url':received_job_obj.uri,'job_id':job_id}
                print_debug_info(f"Request data inside {request_data}") 
                response_obj = requests.post(request_url, data = json.dumps(request_data), headers=headers)
                print_debug_info(response_obj.text)
                if response_obj.status_code == 200:

                    # build live analytic     
                    print_debug_info("> Sending Request for Complianc & Analysis Building")                    
                    analytic_data = build_analytics_and_compliance(category_detail_obj, response_obj.text, shelf_compliance_obj)                        
                    
                    # Update received job status into DONE            
                    bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_DONE,ReceiveJobs.dataResponse:analytic_data})
                    bridge.get_db().get_session().commit()
                elif response_obj.status_code == 400 or response_obj.status_code == 500:
                    # Update received job status into ERROR            
                    bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_ERROR,ReceiveJobs.dataResponse:response_obj.status_code})
                    bridge.get_db().get_session().commit()
            except:
                # Update received job status into ERROR            
                bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_COMMUNICATION_ERROR,ReceiveJobs.dataResponse:"Communication Error"})
                bridge.get_db().get_session().commit()                
        else:
            print_debug_info(f"Job does not proceed {received_job_obj.requestStatus}")
    print_debug_info("updating_pending_job_status")
