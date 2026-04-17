
-- 1. Ensure Projects exist
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane A: Heritage & History', 8, true, 1) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane B: Website & Public Edge', 8, true, 2) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane C: Security & PBS', 8, true, 3) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane D: Stockenweiler Migration', 8, true, 4) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('FraWo Homeserver 2027', 8, true, 5) ON CONFLICT DO NOTHING;

-- 2. Archive legacy masterplan tile
UPDATE project_project SET active = false WHERE name = '🚀 Homeserver 2027: Masterplan';

-- 3. Enable Discounts
INSERT INTO res_groups_users_rel (gid, uid) 
SELECT g.id, 8 FROM res_groups g WHERE g.name = 'Discount on lines' 
ON CONFLICT DO NOTHING;
