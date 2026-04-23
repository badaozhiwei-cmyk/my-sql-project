from sqlalchemy import create_engine, text

def add_indexes():
    engine = create_engine('postgresql://postgres:123456@localhost:5432/sql_course')
    
    with engine.connect() as conn:
        # 设置为自动提交模式，因为创建索引不能在事务块中（部分操作）
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        print("Adding Primary Keys...")
        try:
            conn.execute(text("ALTER TABLE company_dim ADD PRIMARY KEY (company_id);"))
            conn.execute(text("ALTER TABLE job_postings_fact ADD PRIMARY KEY (job_id);"))
        except Exception as e:
            print(f"Note: {e}")

        print("Adding Indexes for faster JOINs and Filtering...")
        try:
            conn.execute(text("CREATE INDEX idx_company_id ON job_postings_fact (company_id);"))
            conn.execute(text("CREATE INDEX idx_job_title_short ON job_postings_fact (job_title_short);"))
            conn.execute(text("CREATE INDEX idx_salary_year_avg ON job_postings_fact (salary_year_avg);"))
        except Exception as e:
            print(f"Note: {e}")
            
    print("Optimization Complete! Your queries should be lightning fast now.")

if __name__ == "__main__":
    add_indexes()
