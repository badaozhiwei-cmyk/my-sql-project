import os

def fix_sql_files():
    scripts_dir = 'scripts'
    files = [f for f in os.listdir(scripts_dir) if f.endswith('.sql')]
    
    for filename in files:
        path = os.path.join(scripts_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复 1: ROUND 函数精度问题
        # 将 ROUND(AVG(...), 0) 替换为 ROUND(AVG(...)::numeric, 0)
        content = content.replace('ROUND(AVG(salary_year_avg), 0)', 'ROUND(AVG(salary_year_avg)::numeric, 0)')
        content = content.replace('ROUND(AVG(salary_year_avg), 2)', 'ROUND(AVG(salary_year_avg)::numeric, 2)')
        
        # 修复 2: GROUP BY 缺失字段问题 (针对 4 和 5 号脚本)
        if 'GROUP BY' in content:
            # 针对 4_top_paying_skills.sql: 确保 GROUP BY 包含 skills_dim.skills
            if '4_top_paying_skills.sql' in filename:
                content = content.replace('GROUP BY\n    skills', 'GROUP BY\n    skills_dim.skill_id, skills_dim.skills')
            
            # 针对 5_optimal_skills.sql: 确保 GROUP BY 包含 skills_dim.skills
            if '5_optimal_skills.sql' in filename:
                # 修复第一个 CTE
                content = content.replace('GROUP BY\n        skills_dim.skill_id', 'GROUP BY\n        skills_dim.skill_id, skills_dim.skills')
                # 修复第二个 CTE
                content = content.replace('GROUP BY\n        average_salary.skill_id', 'GROUP BY\n        average_salary.skill_id, average_salary.skills')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    print(f"Fixed {len(files)} SQL files for PostgreSQL compatibility.")

if __name__ == "__main__":
    fix_sql_files()
