from app import celery
from celery.utils.log import get_task_logger

from bridge.bridge_manager import BridgeManager
from models.modelDetail import AiModelDetail
from models.receiveJobs import ReceiveJobs

from utilities.constant import JOB_STATUS_DONE, JOB_STATUS_ERROR, JOB_STATUS_INSERTED, JOB_STATUS_PENDING

logger = get_task_logger(__name__)

@celery.task()
def process_image(job_id,model_id):
    model_detail_obj = None
    received_job_obj = None

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
        logger.info(f"{job.unProcessedImage}")
        received_job_obj = job
    logger.info(received_job_obj)

    logger.info("checking_pending_job_status")
    if received_job_obj != None:
        if received_job_obj.requestStatus.lower() == JOB_STATUS_INSERTED:
            logger.info(received_job_obj.requestStatus)
            logger.info(f"Updating status value from Inserted to Pending against {job_id}")
            bridge.get_db().get_session().query(ReceiveJobs).filter_by(id = job_id).update({ReceiveJobs.requestStatus:JOB_STATUS_PENDING})
            bridge.get_db().get_session().commit()

            
        else:
            logger.info(f"Job does not proceed {received_job_obj.requestStatus}")
    logger.info("updating_pending_job_status")
