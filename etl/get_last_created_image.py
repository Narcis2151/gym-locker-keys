def get_last_created_image(bq_client):
    query = """
    SELECT max(parse_datetime('%Y-%m-%d %H:%M:%E6S', date_created)) as latest_date
    FROM `gym-locker-keys.gym_locker_data.image_classification`
    """
    query_job = bq_client.query(query)
    results = query_job.result()
    for row in results:
        return row.latest_date
    return None  # If table is empty