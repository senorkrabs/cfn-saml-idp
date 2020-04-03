import logging
import boto3
import urllib3
from botocore.exceptions import ClientError
import cfnresponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    iam_client = boto3.client("iam")
    pass
except Exception as e:
    logger.error('Unable to create IAM client: {}'.format(str(e)))

def get_url(url):
    http = urllib3.PoolManager()
    logger.debug ('Fetching: {}'.format(url))
    r = http.request('GET', url)
    if r.status != 200:
        raise ValueError ('Non-200 HTTP result: {}' )
    return r.data.decode('utf-8')
def build_arn(name):
    return "arn:aws:iam::" + boto3.client('sts').get_caller_identity().get('Account') + ":saml-provider/" + name
def create(name, metadata):
    logger.info("Got Create")   
    provider = iam_client.create_saml_provider(SAMLMetadataDocument=metadata,Name=name)
    logger.info("Arn: {}".format(provider['SAMLProviderArn']))
    return cfnresponse.SUCCESS, {"Arn": provider['SAMLProviderArn']}, provider['SAMLProviderArn']
def update(physical_id, metadata):
    logger.info("Got Update")
    provider = iam_client.update_saml_provider(SAMLMetadataDocument=metadata, SAMLProviderArn=physical_id)
    return cfnresponse.SUCCESS, {"Arn": provider['SAMLProviderArn']}, provider['SAMLProviderArn']
def delete(physical_id):
    logger.info("Got Delete")
    try:
        iam_client.delete_saml_provider(SAMLProviderArn=physical_id)
        logger.info ('Deleted: {}'.format(physical_id))
        return cfnresponse.SUCCESS, {}, physical_id
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchEntity":
            logger.warn('Provider {} does not exist.'.format(physical_id))
            return cfnresponse.SUCCESS, {}, physical_id
        else:
            raise ValueError("Cannot delete SAML provider " + physical_id + ": " + str(e))
def handler(event, context):
    logger.debug(event)
    if iam_client == None:
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Reason': 'Unable to create IAM Client.'})
    try:
        name = event.get('ResourceProperties').get('Name')
        metadata = event.get('ResourceProperties').get('Metadata', '') 
        metadata_url = event.get('ResourceProperties').get('MetadataUrl', '')
        physical_id = event.get('PhysicalResourceId', '')
        if metadata == '' and metadata_url != '':
            metadata = get_url(metadata_url)
        logger.debug("Metadata: {}".format(metadata))   
        if event['RequestType'] == 'Create':
            response, data, physical_id = create(name, metadata)
        elif event['RequestType'] == 'Update':
            if event.get('OldResourceProperties').get('Name') != name:
                response, data, physical_id = create(name, metadata)
            else: response, data, physical_id  = update(physical_id, metadata)
        elif event['RequestType'] == 'Delete':
            response, data, physical_id = delete(physical_id)
        else:
            logger.error('Unknown operation: {}'.format(event['RequestType']))
            raise ValueError ('Unknown Operation.')
        cfnresponse.send(event, context, response, data, physical_id)
    except Exception as e:
        logger.error('Exception: {}'.format(str(e)))
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Reason': str(e)}, physical_id)
        raise