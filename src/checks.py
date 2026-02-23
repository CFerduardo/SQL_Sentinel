#disk space 
QUERY_DISCS = """
    SELECT DISTINCT vs.volume_mount_point, 
    CAST(vs.available_bytes * 100.0 / vs.total_bytes AS DECIMAL(10,2)) AS PCT
    FROM sys.master_files AS mf
    CROSS APPLY sys.dm_os_volume_stats(mf.database_id, mf.file_id) AS vs
"""

#log size
QUERY_LOGS = """
SELECT 
    DB_NAME(database_id) AS [BD],
    CAST((size * 8.0 / 1024.0) AS DECIMAL(10,2)) AS [TotalMB],
    CAST(FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024.0 AS DECIMAL(10,2)) AS [UsedMB],
    CAST((FILEPROPERTY(name, 'SpaceUsed') * 100.0 / size) AS DECIMAL(10,2)) AS [PCT]
FROM sys.master_files
"""


"""
if specific databases are desired

QUERY_LOGS = 
SELECT 
    DB_NAME(database_id) AS [BD],
    CAST((size * 8.0 / 1024.0) AS DECIMAL(10,2)) AS [TotalMB],
    CAST(FILEPROPERTY(name, 'SpaceUsed') * 8.0 / 1024.0 AS DECIMAL(10,2)) AS [UsedMB],
    CAST((FILEPROPERTY(name, 'SpaceUsed') * 100.0 / size) AS DECIMAL(10,2)) AS [PCT]
FROM sys.master_files
WHERE type = 1 AND DB_NAME(database_id) IN ('name_dabatase1', 'name_database2')
"""