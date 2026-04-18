-- Usage:
--   psql -v login=admin -v new_password='SET_AT_RUNTIME' -f scripts/pwd_reset.sql
-- Klartext-Secrets gehoeren nicht ins Repo.
UPDATE res_users
SET password = :'new_password'
WHERE login = :'login';
