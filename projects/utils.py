import requests
import logging

logger = logging.getLogger(__name__)

def register_service():
    service_name = 'projectservice'
    address = 'http://projectservice-backend-1:8001/'  # Change this to your actual service address
    port = 8001  # Port of the project service
    register_url = 'http://servicediscovery-backend-1:8003/service/register/'  # Change this to your service discovery URL

    try:
        response = requests.post(register_url, json={
            'name': service_name,
            'address': address,
            'port': port
        })

        if response.status_code == 201:
            print('Successfully registered the project service')
            logger.info('Successfully registered the project service')
        else:
            print(f'Failed to register the project service: {response.status_code} - {response.text}')
            logger.error(f'Failed to register the project service: {response.status_code} - {response.text}')
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception during service registration: {e}")
        raise

def deregister_service():
    service_name = 'projectservice'
    deregister_url = f'http://servicediscovery-backend-1:8003/service/deregister/{service_name}/'
    
    try:
        response = requests.delete(deregister_url)

        if response.status_code == 204:
            print('Successfully deregistered the project service')
            logger.info('Successfully deregistered the project service')
        else:
            print(f'Failed to deregister the project service: {response.status_code} - {response.text}')
            logger.error(f'Failed to deregister the project service: {response.status_code} - {response.text}')
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception during service deregistration: {e}")
