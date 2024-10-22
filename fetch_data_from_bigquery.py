def fetch_data_from_bigquery(bq_client):
    query = """
    SELECT locker_number
    FROM `gym-locker-keys.gym_locker_data.image_classification`
    """
    query_job = bq_client.query(query)
    results = query_job.result()
    locker_numbers = [row.locker_number for row in results]
    return locker_numbers
