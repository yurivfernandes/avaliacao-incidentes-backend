CREATE PROC [dbo].[PROC_ETL_INCIDENTES_SERVICE_NOW]
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variável para controle de atualização incremental
    DECLARE @data_corte DATETIME = DATEADD(DAY, -10, GETDATE());
    
    -- Inserir novos Assignment Groups
    INSERT INTO dw_analytics.d_assignment_group (id, dv_assignment_group)
    SELECT DISTINCT 
        LTRIM(RTRIM(inc.assignment_group)) AS id,
        LTRIM(RTRIM(inc.dv_assignment_group)) AS dv_assignment_group
    FROM SERVICE_NOW.dbo.incident inc
    LEFT JOIN dw_analytics.d_assignment_group ag 
        ON LTRIM(RTRIM(inc.assignment_group)) = ag.id
    WHERE ag.id IS NULL
        AND inc.assignment_group IS NOT NULL
        AND inc.assignment_group != ''
        AND inc.dv_assignment_group != ''
        AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte);

    -- Inserir novos Resolved By
    INSERT INTO dw_analytics.d_resolved_by (id, dv_resolved_by)
    SELECT DISTINCT
        LTRIM(RTRIM(inc.resolved_by)) AS id,
        LTRIM(RTRIM(inc.dv_resolved_by)) AS dv_resolved_by
    FROM SERVICE_NOW.dbo.incident inc
    LEFT JOIN dw_analytics.d_resolved_by rb 
        ON LTRIM(RTRIM(inc.resolved_by)) = rb.id
    WHERE rb.id IS NULL
        AND inc.resolved_by IS NOT NULL
        AND inc.resolved_by != ''
        AND inc.dv_resolved_by != ''
        AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte);

    -- Inserir novos Contracts
    INSERT INTO dw_analytics.d_contract (id, dv_contract)
    SELECT DISTINCT
        LTRIM(RTRIM(inc.contract)) AS id,
        LTRIM(RTRIM(inc.dv_contract)) AS dv_contract
    FROM SERVICE_NOW.dbo.incident inc
    LEFT JOIN dw_analytics.d_contract c 
        ON LTRIM(RTRIM(inc.contract)) = c.id
    WHERE c.id IS NULL
        AND inc.contract IS NOT NULL
        AND inc.contract != ''
        AND inc.dv_contract != ''
        AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte);

    -- Inserir novas Companies
    INSERT INTO dw_analytics.d_company (id, dv_company, u_cnpj)
    SELECT DISTINCT
        LTRIM(RTRIM(inc.company)) AS id,
        LTRIM(RTRIM(inc.dv_company)) AS dv_company,
        REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(inc.u_cnpj)), '.', ''), '/', ''), '-', '') AS u_cnpj
    FROM SERVICE_NOW.dbo.incident inc
    LEFT JOIN dw_analytics.d_company c 
        ON LTRIM(RTRIM(inc.company)) = c.id
    WHERE c.id IS NULL
        AND inc.company IS NOT NULL
        AND inc.company != ''
        AND inc.dv_company != ''
        AND inc.u_cnpj != ''
        AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte);

    -- Relacionamento Resolved By - Assignment Group
    INSERT INTO dw_analytics.d_resolved_by_assignment_group (resolved_by_id, assignment_group_id)
    SELECT resolved_by_id, assignment_group_id
    FROM (
        SELECT 
            LTRIM(RTRIM(inc.resolved_by)) AS resolved_by_id,
            LTRIM(RTRIM(inc.assignment_group)) AS assignment_group_id,
            ROW_NUMBER() OVER (PARTITION BY LTRIM(RTRIM(inc.resolved_by)), LTRIM(RTRIM(inc.assignment_group)) ORDER BY (SELECT NULL)) AS rn
        FROM SERVICE_NOW.dbo.incident inc
        INNER JOIN dw_analytics.d_resolved_by rb 
            ON LTRIM(RTRIM(inc.resolved_by)) = rb.id
        INNER JOIN dw_analytics.d_assignment_group ag 
            ON LTRIM(RTRIM(inc.assignment_group)) = ag.id
        WHERE inc.resolved_by IS NOT NULL
        AND inc.assignment_group IS NOT NULL
        AND inc.resolved_by != ''
        AND inc.assignment_group != ''
       	AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte)
    ) AS SubQuery
    WHERE rn = 1;

    -- Apagar incidentes abertos e fechados nos últimos 10 dias
    DELETE FROM dw_analytics.f_incident

	--WHERE opened_at >= @data_corte OR closed_at >= @data_corte;
	

    -- Inserir ou atualizar Incidents na tabela fato
    MERGE dw_analytics.f_incident AS target
    USING (
        SELECT 
            inc.number,
            inc.sys_id,
            inc.resolved_by,
            inc.assignment_group,
            inc.opened_at,
            inc.closed_at,
            inc.contract,
            sla_first.has_breached as sla_atendimento,
            sla_resolved.has_breached as sla_resolucao,
            inc.company,
            inc.u_origem,
            inc.dv_u_categoria_da_falha,
            inc.dv_u_sub_categoria_da_falha,
            inc.dv_u_detalhe_sub_categoria_da_falha,
            inc.dv_state,
            inc.u_id_vgr,
            inc.u_id_vantive,
            inc.dv_category,
            inc.dv_subcategory,
            inc.dv_u_detail_subcategory,
            inc.u_tipo_indisponibilidade
        FROM SERVICE_NOW.dbo.incident inc
        LEFT JOIN SERVICE_NOW.dbo.incident_sla sla_first 
            ON inc.sys_id = sla_first.task 
            AND (sla_first.dv_sla LIKE '%VITA] FIRST%' or sla_first.dv_sla LIKE '%VGR] SLA Atendimento%')
        LEFT JOIN SERVICE_NOW.dbo.incident_sla sla_resolved 
            ON inc.sys_id = sla_resolved.task 
            AND (sla_resolved.dv_sla LIKE '%VITA] RESOLVED%' or sla_resolved.dv_sla LIKE '%VGR] SLA Resolução%')
        WHERE inc.number IS NOT NULL
            AND (inc.opened_at >= @data_corte OR inc.closed_at >= @data_corte)
    ) AS source
    ON target.number = source.number
    WHEN MATCHED THEN
        UPDATE SET
            resolved_by = source.resolved_by,
            sys_id = source.sys_id,
            assignment_group = source.assignment_group,
            opened_at = source.opened_at,
            closed_at = source.closed_at,
            contract = source.contract,
            sla_atendimento = source.sla_atendimento,
            sla_resolucao = source.sla_resolucao,
            company = source.company,
            u_origem = source.u_origem,
            dv_u_categoria_da_falha = source.dv_u_categoria_da_falha,
            dv_u_sub_categoria_da_falha = source.dv_u_sub_categoria_da_falha,
            dv_u_detalhe_sub_categoria_da_falha = source.dv_u_detalhe_sub_categoria_da_falha,
            dv_state = source.dv_state,
            u_id_vgr = source.u_id_vgr,
            u_id_vantive = source.u_id_vantive,
            dv_category = source.dv_category,
            dv_subcategory = source.dv_subcategory,
            dv_u_detail_subcategory = source.dv_u_detail_subcategory,
            u_tipo_indisponibilidade = source.u_tipo_indisponibilidade
    WHEN NOT MATCHED THEN
        INSERT (
            number, sys_id, resolved_by, assignment_group, opened_at, closed_at,
            contract, sla_atendimento, sla_resolucao, company,
            u_origem, dv_u_categoria_da_falha, dv_u_sub_categoria_da_falha,
            dv_u_detalhe_sub_categoria_da_falha, dv_state, u_id_vgr, u_id_vantive,
            dv_category, dv_subcategory, dv_u_detail_subcategory, u_tipo_indisponibilidade
        )
        VALUES (
            source.number, source.sys_id, source.resolved_by, source.assignment_group,
            source.opened_at, source.closed_at, source.contract,
            source.sla_atendimento, source.sla_resolucao, source.company,
            source.u_origem, source.dv_u_categoria_da_falha,
            source.dv_u_sub_categoria_da_falha,
            source.dv_u_detalhe_sub_categoria_da_falha,
            source.dv_state, source.u_id_vgr, source.u_id_vantive,
            source.dv_category, source.dv_subcategory, source.dv_u_detail_subcategory,
            source.u_tipo_indisponibilidade
        );

-- Adicionar coluna sys_id na tabela f_incident
ALTER TABLE dw_analytics.f_incident
ADD sys_id NVARCHAR(255);

-- Script para remover as colunas da task
ALTER TABLE dw_analytics.f_incident
DROP COLUMN u_tipo_acionamento,
    u_operadora_integrador,
    u_produto,
    u_protocolo,
    abertura_task,
    encerramento_task,
    u_designa_o_lp;

---***ATUALIZA OS ULTIMOS 10 DIAS DA TABELA DE LOCALIDADES DO SAE


DELETE FROM POWER_BI.dw_analytics.f_sae_localidades WHERE DATA_RFB >= CONVERT(DATE,DATEADD(DAY,-10,GETDATE()))

INSERT dw_analytics.f_sae_localidades
SELECT
*
FROM
OPENQUERY([10.128.223.125],
	'SELECT DISTINCT
		ID_VANTIVE,
		UF,
		CIDADE,
		DATA_RFB
	FROM 
		LK_RELATORIO_12.SAE.SAE.TB_PEDIDOS_DADOS with (nolock)
	WHERE
		STATUS_VANTIVE IN (''RFS Faturável'',''RFS Técnico'', ''RFS Não Faturável'')
		AND
		DATA_RFB >= CONVERT(DATE,DATEADD(DAY,-10,GETDATE()))
')

END;
