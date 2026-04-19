#!/usr/bin/env bash
# consolidate_odoo.sh
# Migrates tasks from FraWo_Live and Recovery_DB to FraWo_GbR

DB_USER="odoo"
TARGET_DB="FraWo_GbR"
WOLF_ID=6

# 1. Ensure Archive Project exists
echo "Ensuring Archive Project (ID 7) exists in $TARGET_DB..."
psql -U $DB_USER -d $TARGET_DB -c "INSERT INTO project_project (id, name, active, color, company_id, privacy_visibility) SELECT 7, '{\"de_DE\": \"Lane Z: Archiv / Historie\", \"en_US\": \"Lane Z: Archive / Legacy\"}', true, 1, 1, 'followers' WHERE NOT EXISTS (SELECT id FROM project_project WHERE id = 7);"

# 2. Function to migrate a database
migrate_db() {
    SRC_DB=$1
    echo "Processing source database: $SRC_DB"
    
    # Get project names and mapping to targets
    # Logic: 1=Masterplan, 2=Lane A, 3=Lane B, 4=Lane C, 5=Lane D, 7=Archive
    # We use a CASE statement in SQL for direct transfer
    
    psql -U $DB_USER -d $TARGET_DB -c "
        INSERT INTO project_task (name, description, project_id, user_id, stage_id, kanban_state, priority, active, company_id)
        SELECT 
            t.name, 
            t.description,
            CASE 
                WHEN p.name::text ILIKE '%Masterplan%' THEN 1
                WHEN p.name::text ILIKE '%FraWo Homeserver 2027%' THEN 1
                WHEN p.name::text ILIKE '%Heritage%' THEN 2
                WHEN p.name::text ILIKE '%Founding%' THEN 2
                WHEN p.name::text ILIKE '%Website%' THEN 3
                WHEN p.name::text ILIKE '%Public Edge%' THEN 3
                WHEN p.name::text ILIKE '%Security%' THEN 4
                WHEN p.name::text ILIKE '%PBS%' THEN 4
                WHEN p.name::text ILIKE '%Stockenweiler%' THEN 5
                ELSE 7 
            END as target_project_id,
            $WOLF_ID,
            t.stage_id,
            t.kanban_state,
            t.priority,
            true,
            1
        FROM dblink('dbname=$SRC_DB user=$DB_USER', 'SELECT p.name, t.name, t.description, t.stage_id, t.kanban_state, t.priority FROM project_task t JOIN project_project p ON t.project_id = p.id') 
        AS t(p_name jsonb, name jsonb, description text, stage_id int, kanban_state varchar, priority varchar);
    " || echo "Note: dblink might not be installed, falling back to export/import method..."
}

# Plan B: Export/Import if dblink is missing (likely)
migrate_db_manual() {
    SRC_DB=$1
    echo "Processing source database (Manual Export): $SRC_DB"
    
    # Export to temp file
    TMP_CSV="/tmp/tasks_$SRC_DB.csv"
    psql -U $DB_USER -d $SRC_DB -t -A -F',' -c "SELECT p.name, t.name, COALESCE(t.description, ''), COALESCE(t.stage_id, 1), COALESCE(t.kanban_state, 'normal'), COALESCE(t.priority, '0') FROM project_task t JOIN project_project p ON t.project_id = p.id" > $TMP_CSV
    
    while IFS=',' read -r p_name t_name t_desc t_stage t_kanban t_prio; do
        # Determine target project ID
        TARGET_ID=7
        [[ "$p_name" =~ "Masterplan" || "$p_name" =~ "FraWo Homeserver 2027" ]] && TARGET_ID=1
        [[ "$p_name" =~ "Heritage" || "$p_name" =~ "Founding" ]] && TARGET_ID=2
        [[ "$p_name" =~ "Website" || "$p_name" =~ "Public Edge" ]] && TARGET_ID=3
        [[ "$p_name" =~ "Security" || "$p_name" =~ "PBS" ]] && TARGET_ID=4
        [[ "$p_name" =~ "Stockenweiler" ]] && TARGET_ID=5
        
        # Insert into target
        psql -U $DB_USER -d $TARGET_DB -c "INSERT INTO project_task (name, description, project_id, user_id, stage_id, kanban_state, priority, active, company_id) VALUES ('$t_name', '$t_desc', $TARGET_ID, $WOLF_ID, $t_stage, '$t_kanban', '$t_prio', true, 1);"
    done < $TMP_CSV
}

migrate_db_manual "Recovery_DB"
migrate_db_manual "FraWo_Live"

echo "Consolidation complete."
