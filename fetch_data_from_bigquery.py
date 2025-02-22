from typing import Tuple


def fetch_data_from_bigquery(bq_client) -> Tuple[list, list]:
    query = """
    SELECT locker_number, gym
    FROM `gym-locker-keys.gym_locker_data.image_classification`
    """
    query_job = bq_client.query(query)
    results = query_job.result()
    locker_numbers = {
        '700_fit': [],
        'sweat': []
    }
    for row in results:
        locker_numbers[row.gym].append(row.locker_number)

    return locker_numbers['700_fit'], locker_numbers['sweat']
