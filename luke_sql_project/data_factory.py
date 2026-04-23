import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import ast
import os

# 1. 数据库配置
DB_CONFIG = {
    "drivername": "postgresql",
    "username": "postgres",
    "password": "123456", 
    "host": "localhost",
    "port": 5432,
    "database": "postgres" # 先连接到默认库
}

def load_data():
    try:
        # 创建连接引擎
        url = URL.create(**DB_CONFIG)
        engine = create_engine(url)

        # 自动创建 sql_course 数据库
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text("DROP DATABASE IF EXISTS sql_course;"))
            conn.execute(text("CREATE DATABASE sql_course;"))
        print("Done: Database 'sql_course' created.")

        # 连接到新创建的数据库
        DB_CONFIG["database"] = "sql_course"
        engine = create_engine(URL.create(**DB_CONFIG))

        # 2. 读取原始数据
        csv_path = 'data/job_postings_fact.csv'
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found! Please run download_data.py first.")
            return
            
        print("Reading large CSV (this may take a moment)...")
        df = pd.read_csv(csv_path)
        
        # 生成唯一的 Job ID (原始数据没有)
        df['job_id'] = range(1, len(df) + 1)

        # 3. 处理公司维度表 (company_dim)
        print("Processing company_dim...")
        companies = df[['company_name']].drop_duplicates().reset_index(drop=True)
        companies['company_id'] = range(1, len(companies) + 1)
        # 重命名为 'name' 以匹配 Luke 的 SQL 脚本
        companies = companies.rename(columns={'company_name': 'name'})
        companies.to_sql('company_dim', engine, if_exists='replace', index=False)
        
        # 将 company_id 映射回主表
        # 标准：使用 left_on 和 right_on 来处理字段名不一致的关联
        df = df.merge(companies, left_on='company_name', right_on='name', how='left')
        # 删掉多出来的 'name' 列
        df = df.drop(columns=['name'])

        # 4. 处理技能维度表 (skills_dim) 和 关联表 (skills_job_dim)
        print("Processing skills and mappings...")
        
        # 解析 job_skills 列 (字符串转列表)
        def parse_skills(x):
            try:
                if pd.isna(x): return []
                return ast.literal_eval(x)
            except:
                return []

        df['skills_list'] = df['job_skills'].apply(parse_skills)
        
        # 提取所有唯一技能
        all_skills = sorted(list(set([skill for sublist in df['skills_list'] for skill in sublist])))
        skills_dim = pd.DataFrame({'skills': all_skills}) # 重命名为 'skills'
        skills_dim['skill_id'] = range(1, len(skills_dim) + 1)
        skills_dim.to_sql('skills_dim', engine, if_exists='replace', index=False)

        # 创建职位-技能关联表
        skill_to_id = dict(zip(skills_dim['skills'], skills_dim['skill_id']))
        job_skills_mapping = []
        
        # 爆炸式拆分职位与技能的对应关系 (仅取前 10 万行演示或处理全部，由于数据大，我们采用高效方式)
        for _, row in df[['job_id', 'skills_list']].iterrows():
            for skill in row['skills_list']:
                if skill in skill_to_id:
                    job_skills_mapping.append({'job_id': row['job_id'], 'skill_id': skill_to_id[skill]})
        
        skills_job_dim = pd.DataFrame(job_skills_mapping)
        skills_job_dim.to_sql('skills_job_dim', engine, if_exists='replace', index=False)

        # 5. 处理职位主表 (job_postings_fact)
        print("Processing job_postings_fact...")
        # 移除已经拆分出去的列和临时列
        cols_to_keep = [
            'job_id', 'job_title_short', 'job_title', 'job_location', 'job_via', 
            'job_schedule_type', 'job_work_from_home', 'search_location', 
            'job_posted_date', 'job_no_degree_mention', 'job_health_insurance', 
            'job_country', 'salary_rate', 'salary_year_avg', 'salary_hour_avg', 'company_id'
        ]
        job_postings_fact = df[cols_to_keep]
        
        # 转换日期格式
        job_postings_fact['job_posted_date'] = pd.to_datetime(job_postings_fact['job_posted_date'])
        
        # 导入主表
        job_postings_fact.to_sql('job_postings_fact', engine, if_exists='replace', index=False)

        print("\n" + "="*30)
        print("SUCCESS: Data Factory Finished!")
        print(f"Total Jobs: {len(job_postings_fact)}")
        print(f"Total Companies: {len(companies)}")
        print(f"Total Skills: {len(skills_dim)}")
        print("="*30)

    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    load_data()
