SELECT creation_time, query FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_USER` WHERE job_type = 'QUERY' ORDER BY creation_time DESC LIMIT 10
