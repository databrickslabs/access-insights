CREATE MATERIALIZED VIEW IF NOT EXISTS slog.default.azure_storage_logs_vw
AS
(
  SELECT
    to_timestamp(sl.time) `Storage_Time`,
    case
      when it.table_name is not null then 1
      else 0
    end as `Match_Found`,
    properties.clientRequestId `Storage_ClientRequestId`,
    properties.userAgentHeader `Storage_userAgentHeader`,
    protocol `Storage_Protocol`,
    correlationId `Storage_CorrelationId`,
    identity.type `Storage_AuthenticationType`,
    sl.identity.requester.tenantId `Storage_TenantId`,
    sl.identity.requester.objectId `Storage_PrincipalId`,
    sl.statusText `Storage_StatusText`,
    sl.operationName `Storage_OperationName`,
    regexp_extract(identity.authorization[0].action, '[^/]+$', 0) `Storage_Action`,
    sl.callerIpAddress `Storage_CallerIpAddress`,
    sl.properties.accountName `Storage_AccountName`,
    sl.properties.objectKey `Storage_RelativePath`,
    it.parsed_path `IT_ParsedPath`,
    it.table_name `IT_TableName`,
    it.table_type `IT_TableType`
  FROM
    slog.default.azure_raw_storage_logs sl
      left join (
        select
          concat(table_catalog, '.', table_schema, '.', table_name) as table_name,
          storage_path,
          CONCAT(
            '/',
            regexp_extract(storage_path, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 2),
            '/',
            regexp_extract(storage_path, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 1),
            '/',
            regexp_extract(storage_path, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 4)
          ) `parsed_path`,
          table_type,
          table_owner created_by,
          last_altered_by,
          data_source_format,
          storage_sub_directory
        from
          system.information_schema.tables
        where
          table_catalog <> 'system'
          and storage_path is not null
        union
        select
          concat(volume_catalog, '.', volume_schema, '.', volume_name) as volume_name,
          storage_location,
          CONCAT(
            '/',
            regexp_extract(storage_location, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 2),
            '/',
            regexp_extract(storage_location, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 1),
            '/',
            regexp_extract(storage_location, 'abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?', 4)
          ) `parsed_path`,
          volume_type,
          volume_owner created_by,
          last_altered_by,
          'unstructured' data_source_format,
          '' storage_sub_directory
        from
          system.information_schema.volumes
        where
          volume_catalog <> 'system'
          and storage_location is not null
      ) it
        on sl.properties.objectKey like concat('%', it.parsed_path, '%')
);

REFRESH MATERIALIZED VIEW slog.default.azure_storage_logs_vw;
