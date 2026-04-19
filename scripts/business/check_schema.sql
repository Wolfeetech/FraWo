SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'project_task' 
AND (column_name LIKE '%state%' OR column_name LIKE '%kanban%');
