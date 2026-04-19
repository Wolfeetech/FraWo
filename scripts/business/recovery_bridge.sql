
-- Mission Recovery Script
-- Lane IDs (Verified in Previous UI Audits)

-- Heritage & History (Lane A)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane A: Heritage & History' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Gründung%' OR name ILIKE '%Notar%' OR name ILIKE '%Heritage%';

-- Website & Public Edge (Lane B)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane B: Website & Public Edge' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Website%' OR name ILIKE '%Cloudflare%' OR name ILIKE '%Caddy%' OR name ILIKE '%Domain%';

-- Security & PBS (Lane C)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane C: Security & PBS' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Security%' OR name ILIKE '%Backup%' OR name ILIKE '%PBS%' OR name ILIKE '%Vaultwarden%';

-- Stockenweiler (Lane D)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane D: Stockenweiler Migration' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Stockenweiler%' OR name ILIKE '%Remote%' OR name ILIKE '%Hardware%';

-- Everything Else -> Homeserver
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'FraWo Homeserver 2027' LIMIT 1), user_ids = array[7], active = true
WHERE project_id IS NULL OR project_id NOT IN (SELECT id FROM project_project WHERE name LIKE 'Lane %');

-- Ensure Starred for Wolf (User 7 IS the active wolf ID from UI check)
UPDATE project_project SET favorite_user_ids = array_append(favorite_user_ids, 7) WHERE NOT 7 = ANY(COALESCE(favorite_user_ids, ARRAY[]::integer[]));
