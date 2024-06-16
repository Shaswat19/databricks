import requests
import os
source_token = os.environ.get('DEV_DATABRICKS_TOKEN')
source_instance = os.environ.get('DEV_DATABRICKS_INSTANCE')
target_token = os.environ.get('STAGING_DATABRICKS_TOKEN')
target_instance = os.environ.get('DATABRICKS_STAGING_TOKEN')
# source_token = 'dapi25febb2d20c24e480fa3d57c736563a5'
# source_instance = 'dbc-379f39be-a8ea.cloud.databricks.com'
# target_token = 'dapia3a2d9dff4d05ad0ffe401e8df5e50bb'
# target_instance = 'dbc-1ff63931-7920.cloud.databricks.com'

target_cluster_id = "0614-110917-8ckf6rqe"


# Headers for API requests
headers_source = {
    'Authorization': f'Bearer {source_token}',
    'Content-Type': 'application/json'
}

headers_target = {
    'Authorization': f'Bearer {target_token}',
    'Content-Type': 'application/json'
}

# Function to list jobs in the environment
def list_jobs(instance, headers):
    response = requests.get(f'https://{instance}/api/2.0/jobs/list', headers=headers)
    response.raise_for_status()
    return response.json().get('jobs', [])

# Function to get job configuration
def get_job_config(instance, headers, job_id):
    response = requests.get(f'https://{instance}/api/2.0/jobs/get?job_id={job_id}', headers=headers)
    response.raise_for_status()
    return response.json()

# Function to create job in the target environment
def create_job(instance, headers, job_config):
    response = requests.post(f'https://{instance}/api/2.0/jobs/create', headers=headers, json=job_config)
    response.raise_for_status()
    return response.json()

# Function to update job in the target environment
def update_job(instance, headers, job_id, job_config):
    response = requests.post(f'https://{instance}/api/2.0/jobs/update?job_id={job_id}', headers=headers, json=job_config)
    response.raise_for_status()
    return response.json()

# Function to filter jobs by name
def filter_jobs_by_name(jobs, name):
    return [job for job in jobs if job['settings']['name'] == name]

# Function to export a job
def export_job(job, target_jobs, target_cluster_id, display_job_config = False) -> str:
    error_message = ''
    try:
        job_id = job['job_id']
        job_name = job['settings']['name']

        print(f"\nExporting job: {job_name}") 

        # Get job configuration from the source environment
        job_config = get_job_config(source_instance, headers_source, job_id)
       
        # Check if the job already exists in the target environment
        target_job = filter_jobs_by_name(target_jobs, job_name)

        # Prepare the job configuration
        job_config.pop('job_id', None)
        target_owner_email = job_config['creator_user_name']
        print('target_owner_email ',target_owner_email)
        job_config['creator_user_name']=target_owner_email
        job_config['run_as_user_name'] = target_owner_email

        job_settings = job_config.get('settings', {})
        tasks = job_settings.pop('tasks', [])

        # Remove the settings
        job_config.pop('settings', None)

        # Copy settings contents to root level
        for key, value in job_settings.items():
            job_config[key] = value

        # Update cluster ID in tasks
        for task in tasks:
            if 'existing_cluster_id' in task:
                task['existing_cluster_id'] = target_cluster_id
        # Add tasks to the root level
        job_config['tasks'] = tasks

        if target_job:
            target_job_id = target_job[0]['job_id']
            update_job(target_instance, headers_target, target_job_id, job_config)
        else:
            create_job(target_instance, headers_target, job_config)
    except Exception as e:
        error_message = f"Job with name '{job_name}' failed to export. Error: {e}"
        print(error_message)
    finally:
        print(f"Finished processing: {job_name}")    
        if display_job_config:
            print(f"\nOriginal job: {job_config}\n")
            print(f"Modified job: {job_config}\n") 
        return error_message


# Function to export all jobs
def export_all_jobs(display_job_config = False):

    source_jobs = list_jobs(source_instance, headers_source)
    target_jobs = list_jobs(target_instance, headers_target)

    for job in source_jobs:
      export_job(job, target_jobs, target_cluster_id, display_job_config)
    

# Function to export jobs by name
def export_jobs_by_name(job_name):
    source_jobs = list_jobs(source_instance, headers_source)
    target_jobs = list_jobs(target_instance, headers_target)

    filtered_jobs = filter_jobs_by_name(source_jobs, job_name)

    if not filtered_jobs:
        print(f"No jobs found with name '{job_name}' in the source environment.")
        return

    for job in filtered_jobs:
        export_job(job, target_jobs, target_cluster_id)
                
    print(f"Jobs with name '{job_name}' have been processed.")


export_all_jobs()
