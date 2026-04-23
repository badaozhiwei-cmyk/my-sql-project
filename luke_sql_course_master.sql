/*
================================================================================
【Luke Barousse SQL 数据分析课程 - 知识点全库】
================================================================================
这个文件整合了从环境初始化到高级表操作的所有知识点。
按照课程逻辑排序，建议分块执行。
*/

-- =============================================================================
-- 第一部分：基础建表 (DDL - Data Definition Language)
-- 知识点：CREATE TABLE, PRIMARY KEY, 数据类型
-- =============================================================================

-- 1. 创建职位表 (job_postings_fact)
CREATE TABLE IF NOT EXISTS job_postings_fact (
    job_id INT PRIMARY KEY,              -- 职位ID，设为主键（唯一且不为空）
    company_id INT,                      -- 公司ID
    job_title_short VARCHAR(255),        -- 职位简称
    job_title VARCHAR(255),              -- 职位全称
    job_location VARCHAR(255),           -- 工作地点
    job_via VARCHAR(255),                -- 招聘渠道
    job_schedule_type VARCHAR(255),      -- 工作性质（全职/兼职）
    job_work_from_home BOOLEAN,          -- 是否远程
    search_location VARCHAR(255),        -- 搜索地点
    job_posted_date TIMESTAMP,           -- 发布日期
    job_no_degree_mention BOOLEAN,       -- 是否不需要学位
    job_health_insurance_mention BOOLEAN,-- 是否包含医疗保险
    job_country VARCHAR(255),            -- 国家
    salary_year_avg NUMERIC,             -- 平均年薪
    salary_hour_avg NUMERIC              -- 平均时薪
);

-- 2. 创建技能维度表 (skills_dim)
CREATE TABLE IF NOT EXISTS skills_dim (
    skill_id INT PRIMARY KEY,
    skills VARCHAR(255),
    type VARCHAR(255)
);

-- 3. 创建职位-技能关联表 (skills_job_dim)
CREATE TABLE IF NOT EXISTS skills_job_dim (
    job_id INT,
    skill_id INT,
    PRIMARY KEY (job_id, skill_id)       -- 复合主键：保证一对关系只出现一次
);


-- =============================================================================
-- 第二部分：数据操作 (DML - Data Manipulation Language)
-- 知识点：INSERT, UPDATE, SELECT
-- =============================================================================

-- 1. 修改现有数据 (UPDATE)
-- 场景：给 job_id 为 102 的职位修改年薪
UPDATE job_postings_fact
SET salary_year_avg = 105000
WHERE job_id = 102;

-- 2. 验证查询 (SELECT)
SELECT * FROM job_postings_fact;


-- =============================================================================
-- 第三部分：表结构进阶修改 (DDL - ALTER TABLE)
-- 知识点：ADD, RENAME, ALTER TYPE, DROP COLUMN
-- =============================================================================

-- 1. 增加新列 (ADD)
-- 场景：需要记录联系人姓名
ALTER TABLE job_postings_fact
ADD contact_name TEXT;

-- 2. 修改数据以填充新列
UPDATE job_postings_fact
SET contact_name = 'Luke Barousse'
WHERE job_id = 103;

-- 3. 重命名列 (RENAME)
-- 场景：觉得 contact_name 不够专业，改名为 hiring_manager
ALTER TABLE job_postings_fact
RENAME COLUMN contact_name TO hiring_manager;

-- 4. 修改列类型 (ALTER COLUMN TYPE)
-- 场景：将 hiring_manager 从 TEXT 改为更规范的 VARCHAR(50)
ALTER TABLE job_postings_fact
ALTER COLUMN hiring_manager TYPE VARCHAR(50);

-- 5. 删除列 (DROP COLUMN)
-- 场景：业务变更，不再需要记录招聘经理
ALTER TABLE job_postings_fact
DROP COLUMN hiring_manager;


-- =============================================================================
-- 第四部分：数据清理 (DDL)
-- 知识点：DROP TABLE
-- =============================================================================

-- 验证：在删除前最后看一眼表
SELECT * FROM job_postings_fact;

-- 彻底删除表（谨慎操作！）
-- DROP TABLE job_postings_fact;
