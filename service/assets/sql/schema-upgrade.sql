-- Database compatibility upgrades for existing installations.
-- SQLModel creates complete schemas for new databases; this file only upgrades
-- columns and constraints that create_all() cannot add to existing tables.

SET NAMES utf8mb4;
SET time_zone = '+08:00';

-- Add the department reference introduced after the initial users table.
SET @dept_id_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'dept_id'
);
SET @add_dept_id_sql = IF(
    @dept_id_exists = 0,
    'ALTER TABLE users ADD COLUMN dept_id INT NULL',
    'SELECT 1'
);
PREPARE add_dept_id_stmt FROM @add_dept_id_sql;
EXECUTE add_dept_id_stmt;
DEALLOCATE PREPARE add_dept_id_stmt;

SET @dept_id_index_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND INDEX_NAME = 'ix_users_dept_id'
);
SET @add_dept_id_index_sql = IF(
    @dept_id_index_exists = 0,
    'CREATE INDEX ix_users_dept_id ON users (dept_id)',
    'SELECT 1'
);
PREPARE add_dept_id_index_stmt FROM @add_dept_id_index_sql;
EXECUTE add_dept_id_index_stmt;
DEALLOCATE PREPARE add_dept_id_index_stmt;

-- Normalize nullable roots before adding self-referencing constraints.
SET @department_parent_nullable = (
    SELECT IS_NULLABLE
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'departments'
      AND COLUMN_NAME = 'parent_id'
);
SET @alter_department_parent_sql = IF(
    @department_parent_nullable = 'NO',
    'ALTER TABLE departments MODIFY COLUMN parent_id INT NULL DEFAULT NULL',
    'SELECT 1'
);
PREPARE alter_department_parent_stmt FROM @alter_department_parent_sql;
EXECUTE alter_department_parent_stmt;
DEALLOCATE PREPARE alter_department_parent_stmt;

-- Remove orphaned references before enforcing foreign keys.
UPDATE users AS u
LEFT JOIN roles AS r ON r.id = u.role_id
SET u.role_id = NULL
WHERE u.role_id IS NOT NULL
  AND r.id IS NULL;

UPDATE users AS u
LEFT JOIN departments AS d ON d.dept_id = u.dept_id
SET u.dept_id = NULL
WHERE u.dept_id IS NOT NULL
  AND d.dept_id IS NULL;

UPDATE departments
SET parent_id = NULL
WHERE parent_id = 0
   OR parent_id = dept_id;

UPDATE departments AS d
LEFT JOIN departments AS p ON p.dept_id = d.parent_id
SET d.parent_id = NULL
WHERE d.parent_id IS NOT NULL
  AND p.dept_id IS NULL;

UPDATE menu
SET parent_id = NULL
WHERE parent_id = 0
   OR parent_id = menu_id;

UPDATE menu AS m
LEFT JOIN menu AS p ON p.menu_id = m.parent_id
SET m.parent_id = NULL
WHERE m.parent_id IS NOT NULL
  AND p.menu_id IS NULL;

UPDATE login_logs AS l
LEFT JOIN users AS u ON u.id = l.user_id
SET l.user_id = NULL
WHERE l.user_id IS NOT NULL
  AND u.id IS NULL;

UPDATE operation_logs AS l
LEFT JOIN users AS u ON u.id = l.user_id
SET l.user_id = NULL
WHERE l.user_id IS NOT NULL
  AND u.id IS NULL;

UPDATE exception_logs AS l
LEFT JOIN users AS u ON u.id = l.user_id
SET l.user_id = NULL
WHERE l.user_id IS NOT NULL
  AND u.id IS NULL;

DELETE ur
FROM user_role AS ur
LEFT JOIN users AS u ON u.id = ur.user_id
LEFT JOIN roles AS r ON r.id = ur.role_id
WHERE u.id IS NULL
   OR r.id IS NULL;

DELETE rm
FROM role_menu AS rm
LEFT JOIN roles AS r ON r.id = rm.role_id
LEFT JOIN menu AS m ON m.menu_id = rm.menu_id
WHERE r.id IS NULL
   OR m.menu_id IS NULL;

DELETE up
FROM user_post AS up
LEFT JOIN users AS u ON u.id = up.user_id
LEFT JOIN posts AS p ON p.post_id = up.post_id
WHERE u.id IS NULL
   OR p.post_id IS NULL;

-- Add each foreign key only when the same relationship does not already exist.
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'role_id'
      AND REFERENCED_TABLE_NAME = 'roles'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE users ADD CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'dept_id'
      AND REFERENCED_TABLE_NAME = 'departments'
      AND REFERENCED_COLUMN_NAME = 'dept_id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE users ADD CONSTRAINT fk_users_department FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user_role'
      AND COLUMN_NAME = 'user_id'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE user_role ADD CONSTRAINT fk_user_role_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user_role'
      AND COLUMN_NAME = 'role_id'
      AND REFERENCED_TABLE_NAME = 'roles'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE user_role ADD CONSTRAINT fk_user_role_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'role_menu'
      AND COLUMN_NAME = 'role_id'
      AND REFERENCED_TABLE_NAME = 'roles'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE role_menu ADD CONSTRAINT fk_role_menu_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'role_menu'
      AND COLUMN_NAME = 'menu_id'
      AND REFERENCED_TABLE_NAME = 'menu'
      AND REFERENCED_COLUMN_NAME = 'menu_id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE role_menu ADD CONSTRAINT fk_role_menu_menu FOREIGN KEY (menu_id) REFERENCES menu(menu_id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user_post'
      AND COLUMN_NAME = 'user_id'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE user_post ADD CONSTRAINT fk_user_post_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user_post'
      AND COLUMN_NAME = 'post_id'
      AND REFERENCED_TABLE_NAME = 'posts'
      AND REFERENCED_COLUMN_NAME = 'post_id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE user_post ADD CONSTRAINT fk_user_post_post FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE RESTRICT',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'departments'
      AND COLUMN_NAME = 'parent_id'
      AND REFERENCED_TABLE_NAME = 'departments'
      AND REFERENCED_COLUMN_NAME = 'dept_id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE departments ADD CONSTRAINT fk_departments_parent FOREIGN KEY (parent_id) REFERENCES departments(dept_id) ON DELETE RESTRICT',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'menu'
      AND COLUMN_NAME = 'parent_id'
      AND REFERENCED_TABLE_NAME = 'menu'
      AND REFERENCED_COLUMN_NAME = 'menu_id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE menu ADD CONSTRAINT fk_menu_parent FOREIGN KEY (parent_id) REFERENCES menu(menu_id) ON DELETE CASCADE',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'login_logs'
      AND COLUMN_NAME = 'user_id'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE login_logs ADD CONSTRAINT fk_login_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'operation_logs'
      AND COLUMN_NAME = 'user_id'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE operation_logs ADD CONSTRAINT fk_operation_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;

SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'exception_logs'
      AND COLUMN_NAME = 'user_id'
      AND REFERENCED_TABLE_NAME = 'users'
      AND REFERENCED_COLUMN_NAME = 'id'
);
SET @add_fk_sql = IF(
    @fk_exists = 0,
    'ALTER TABLE exception_logs ADD CONSTRAINT fk_exception_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE add_fk_stmt FROM @add_fk_sql;
EXECUTE add_fk_stmt;
DEALLOCATE PREPARE add_fk_stmt;
