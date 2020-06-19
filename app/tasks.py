from app import celery
from celery.utils.log import get_task_logger

from bridge.bridge_manager import BridgeManager
from models.modelDetail import AiModelDetail
from models.receiveJobs import ReceiveJobs
from models.category import Category
from models.subcategory import SubCategory
from utilities.category_Detail import CategoryDetail
from utilities.category_Response import CategoryResponse
from utilities.brand_Response import BrandResponse

from utilities.constant import JOB_STATUS_DONE, JOB_STATUS_ERROR, JOB_STATUS_INSERTED, JOB_STATUS_PENDING, JOB_STATUS_COMMUNICATION_ERROR

from utilities.common import get_url
import requests
import json

logger = get_task_logger(__name__)


def build_analytics(category_detail_obj, model_response):
    response_obj = requests.get("http://knowhow.markematics.net/ReceiveJobs/GetJobDetailById/2")
    logger.info(response_obj.text)

    actual_group_data = None
    actual_group_name = []
    category_response = []    
    model_response_json = json.loads(response_obj.text) # json.loads(model_response)
    model_response_json = json.loads(model_response_json['data'])
    logger.info(type(model_response_json))

    for key in model_response_json:
        dic1 = model_response_json[key][0]
        data_response_json = json.loads(dic1['dataresponse'])
        group_data = data_response_json['GroupData']
        print(len(group_data))
        for v in group_data:            
            actual_group_data = json.loads(v)            
            #print(actual_group_data)
            for each_key in actual_group_data:
                #print((each_key['BRAND']))
                actual_group_name.append(each_key['BRAND'])
        #print(type(ungroup_data)) 
    
    # print(" ======== ")
    # print(actual_group_name)
    # print(" ======== ")
    print(actual_group_data)
    for cat_obj in category_detail_obj:        
        print(cat_obj.category_name + " " +cat_obj.subcategory_name)
        tages = cat_obj.tages.split(",")
        # print("*******")
        # print((tages))
        # print("*******")

        print("+++++++++++++")               
        not_found_brand = list(set(tages)-set(actual_group_name))
        found_brand = list(set(tages)-set(not_found_brand)) 
        print(found_brand)
        print(not_found_brand)
        print("+++++++++++++")

       
        temp_tags_counter = []
        for fb in found_brand:
            #print(fb)
            ag_data_item = next(item for item in actual_group_data if item["BRAND"] == fb)
            #print(ag_data_item['BRAND'])
            temp_tags_counter.append(BrandResponse(ag_data_item['BRAND'], ag_data_item['COUNT']))
            #for ag_data in actual_group_data:
                #print(type(ag_data))                
                #s = next((x for x in actual_group_data if x['Brand'] == fb),None)
                #print(ag_data)
        for nfb in not_found_brand:
            temp_tags_counter.append(BrandResponse(nfb,0))
        print("++=====+=====++")
        for tag_counter in temp_tags_counter:
            print(tag_counter.brand_name + " "+ str(tag_counter.count_data))

        category_response.append(CategoryResponse(cat_obj.category_name , cat_obj.subcategory_name, temp_tags_counter))

        print("++===== Response =====++")
        for res in category_response:
            print("------------------------------------")
            print(json.dumps(res.toJson()))

        # temp_tags_counter = []
        # for each_key in actual_group_data:
        #     print((each_key['BRAND']))
        #     if any(each_key['BRAND'] in s for s in tages):
        #         print("yes found "+each_key['BRAND']+" ===>")
        #         temp_tags_counter.append(CategoryResponse(each_key['BRAND']+" ===>", each_key['COUNT']))
        #     else:
        #         print("Not found")
        #         #temp_tags_counter.append(CategoryResponse(each_key['BRAND'], 0))            
                
        #     # convert into list                
        #     temp_brand_lst = [each_key['BRAND']]
        #     not_found_brand = list(set(tages)-set(temp_brand_lst))
        #     print("Not_Found_Brand -->")
        #     print(not_found_brand)
        #         #for nt_brand in not_found_brand:
        #             #temp_tags_counter.append(CategoryResponse(nt_brand, 0))

        # for df in temp_tags_counter:
        #     print("===>"+df.subcategory_name + " "+ str(df.count_data))


    pass

@celery.task()
def process_image(job_id, model_id, project_id):
    model_detail_obj = None
    received_job_obj = None

    category_detail_obj = []

    logger.info("process_image_call")
    bridge = BridgeManager().get_Instance().get_Bridge()
    
    logger.info("getting_model_detail_call")    
    model_details = bridge.get_db().get_session().query(AiModelDetail).filter(AiModelDetail.modelID == model_id)

    for model in model_details:
        logger.info(f"{model.id} {model.port} {model.url} {model.version} {model.modelJson} {model.status} {model.modelID}")
        model_detail_obj = model
    logger.info(model_detail_obj)
    
    logger.info("getting_job_detail")
    received_jobs = bridge.get_db().get_session().query(ReceiveJobs).filter(ReceiveJobs.id == job_id)
    for job in received_jobs:
        logger.info(f"{job.unProcessedImage} {job.uri}")
        received_job_obj = job
    logger.info(received_job_obj)

    logger.info("category_and_subcategory_loading")
    category_obj = bridge.get_db().get_session().query(Category).filter(Category.projectId == project_id)
    for category in category_obj:
        logger.info(f"{category.categoryName}")        
        sub_category_obj = bridge.get_db().get_session().query(SubCategory).filter(SubCategory.categoryId == category.id)   
        for sub_category in sub_category_obj:
            logger.info(f"{sub_category.name}")
            category_detail_obj.append(CategoryDetail(category.id, category.categoryName, category.categoryDescription, sub_category.id, sub_category.name, sub_category.tages))

    # temp analytics
    build_analytics(category_detail_obj,"")

    logger.info("checking_pending_job_status")
    if received_job_obj != None:
        # Checking received job status
        if received_job_obj.requestStatus.lower() == JOB_STATUS_INSERTED:
            logger.info(received_job_obj.requestStatus)
            logger.info(f"Updating status value from Inserted to Pending against {job_id}")

            # Update received job status into PENDING            
            bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_PENDING})
            bridge.get_db().get_session().commit()
            
            # Generating image processing request url
            request_url = get_url(model_detail_obj.url, model_detail_obj.port, "upload-image")

            logger.info(f"Generating image processing request url {request_url}")
            try:
                # Sending image to model for analysis
                headers = {'Content-type': 'application/json'}
                request_data = {'data_url':received_job_obj.uri,'job_id':job_id}
                logger.info(f"Request data inside {request_data}") 
                response_obj = requests.post(request_url, data = json.dumps(request_data), headers=headers)
                logger.info(response_obj.text)
                if response_obj.status_code == 200:
                    # build analytic     
                    #build_analytic(category_detail_obj,response_obj.text)

                    # Update received job status into DONE            
                    bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_DONE,ReceiveJobs.dataResponse:response_obj.text})
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
            logger.info(f"Job does not proceed {received_job_obj.requestStatus}")
    logger.info("updating_pending_job_status")
