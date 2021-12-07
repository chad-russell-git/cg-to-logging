import io
import oci
import json
import logging
from datetime import datetime
from fdk import response

def get_signer():
    signer = None
    try:
        signer = oci.auth.signers.get_resource_principals_signer()
    except Exception as ex:
        LOGGER.error('ERROR: Could not get signer from resource principal', ex, flush=True)
        raise
    return signer

def get_function_config(ctx):
    config = dict(ctx.Config())
    # Getting LOG_LEVEL from function config
    try:
        log_level = getattr(logging,config["LOG_LEVEL"].upper(),None)
        if isinstance(log_level, int):
            LOGGER.setLevel(level=log_level)
        else:
            LOGGER.warning("Invalid LOG_LEVEL in function configuration.")    
    except KeyError:
        LOGGER.warning("LOG_LEVEL not defined in function configuration.")
    
    # Getting LOGGING_OCID from function config
    global LOGGING_OCID
    try:
        LOGGER.info(config["LOGGING_OCID"])
        LOGGING_OCID = config["LOGGING_OCID"]
    except (Exception) as ex:
        raise Exception("Event type LOGGING_OCID Required." + str(ex))
    
def write_event_to_log(signer,event,log_ocid):
    try:
        # Create Log Client from Signer
        log_client = oci.loggingingestion.LoggingClient(config={}, signer=signer)
        # Matching event time precision to match log time precision
        raw_time = event['eventTime']
        updated_time = raw_time.replace('Z','.000Z')
        # Creating Log Entry
        log_entry = oci.loggingingestion.models.LogEntry()
        log_entry.data = json.dumps(event['data'])
        log_entry.id = event['data']['resourceId']
        log_entry.time = updated_time
        # Creating Batch entry
        log_batch = oci.loggingingestion.models.LogEntryBatch()
        log_batch.defaultlogentrytime = updated_time
        log_batch.entries = [log_entry]
        log_batch.source = event['source']
        log_batch.subject = event['data']['resourceName']
        log_batch.type = event['eventType']
        log_details = oci.loggingingestion.models.PutLogsDetails()
        log_details.log_entry_batches = [log_batch]
        log_details.specversion="1.0"
        try: 
            log_client.put_logs(log_ocid, log_details)
            return
        except (Exception) as ex:
            raise Exception('ERROR: Failed to write event to Log: ', ex, flush=True)
    except (Exception) as ex:
        raise Exception ('ERROR: Event format is not correct: ', ex, flush=True)


def handler(ctx, data: io.BytesIO = None):

    global LOGGER
    LOGGER = logging.getLogger()
    LOGGER.setLevel(level=logging.WARNING)
    LOGGER.info("Inside Event Logging Function")

    # Getting function configuration
    get_function_config(ctx)
    
    # Getting Event Message
    try:
        body = json.loads(data.getvalue())
    except (Exception) as ex:
        raise Exception("Event type not properly formatted." + str(ex))

    # Getting Resource principal 
    signer = get_signer()
    
    write_event_to_log(signer, body, LOGGING_OCID)
    
    return response.Response(
        ctx, response_data=json.dumps( {"message": "Wrote Event to Log" }), 
        headers={"Content-Type": "application/json"})



    
