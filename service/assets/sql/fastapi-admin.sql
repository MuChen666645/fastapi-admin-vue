-- FastAPI Admin built-in seed data.
-- This script is idempotent and never overwrites existing operational data.

SET NAMES utf8mb4;
SET time_zone = '+08:00';

-- ---------------------------------------------------------------------------
-- 1. Roles and organization reference data
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO roles (
    id, name, code, description, create_time, update_time, status
) VALUES
    (1, '超级管理员', 'admin', '系统内置超级管理员角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '1'),
    (2, '普通管理员', 'common', '系统内置普通管理员角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '1');

INSERT IGNORE INTO departments (
    dept_id, parent_id, ancestors, dept_name, order_num, leader,
    phone, email, status, create_time, update_time
) VALUES
    (100, NULL, '0', '集团总部', 0, '管理员', '13800000000', 'admin@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (101, 100, '0,100', '研发中心', 1, '研发负责人', '13800000001', 'rd@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (102, 101, '0,100,101', '前端研发部', 1, '前端负责人', '13800000002', 'frontend@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (103, 101, '0,100,101', '后端研发部', 2, '后端负责人', '13800000003', 'backend@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (104, 100, '0,100', '运维部', 2, '运维负责人', '13800000004', 'ops@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (105, 100, '0,100', '财务部', 3, '财务负责人', '13800000005', 'finance@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (106, 100, '0,100', '人力资源部', 4, '人事负责人', '13800000006', 'hr@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT IGNORE INTO posts (
    post_id, post_code, post_name, post_sort, status, remark,
    create_time, update_time
) VALUES
    (100, 'general_manager', '总经理', 1, '1', '公司负责人', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (101, 'developer', '研发工程师', 2, '1', '产品研发岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (102, 'test_engineer', '测试工程师', 3, '1', '质量保障岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (103, 'operations', '运维工程师', 4, '1', '系统运维岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (104, 'finance', '财务专员', 5, '1', '财务管理岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (105, 'human_resources', '人事专员', 6, '1', '人力资源岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ---------------------------------------------------------------------------
-- 2. Built-in users and their relationships
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO users (
    id, create_time, username, password, email, phone, role_id, dept_id,
    nickname, sex, avatar, update_time, status
) VALUES
    (1, CURRENT_TIMESTAMP, 'admin', '$5$rounds=535000$ZOQUh73DBElH3Hff$BpUOeegYosS8Y0VbHqFM.fNAxdyBUN1yHUcUKWJUSx6', 'fastapi-admin@136.com', '13688888888', 1, 100, 'fastapi-admin', '1', '', CURRENT_TIMESTAMP, '1'),
    (2, CURRENT_TIMESTAMP, 'test', '$5$rounds=535000$ZOQUh73DBElH3Hff$BpUOeegYosS8Y0VbHqFM.fNAxdyBUN1yHUcUKWJUSx6', 'fastapi-test@136.com', '13588888888', 2, 101, 'fastapi-user', '1', '', CURRENT_TIMESTAMP, '1');

INSERT IGNORE INTO user_role (user_id, role_id) VALUES
    (1, 1),
    (2, 2);

INSERT IGNORE INTO user_post (user_id, post_id) VALUES
    (1, 100),
    (2, 101);

-- ---------------------------------------------------------------------------
-- 3. Menus and button permissions
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO menu (
    menu_id, parent_id, menu_name, icon, menu_path, component,
    is_hidden, is_cache, menu_type, sort, link_url, perms, status,
    create_time, update_time, remark
) VALUES
    (1, NULL, '首页', '#', 'dashboard', 'home/index', '0', '1', 'C', 1, NULL, 'dashboard', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '首页菜单'),
    (2, NULL, '系统管理', '#', 'system', NULL, '0', '1', 'C', 10, NULL, 'system', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统管理目录'),
    (3, 2, '用户管理', '#', 'user', 'system/user/index', '0', '1', 'C', 1, NULL, 'system:user:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户管理菜单'),
    (4, 2, '角色管理', '#', 'role', 'system/role/index', '0', '1', 'C', 2, NULL, 'system:role:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色管理菜单'),
    (5, 2, '菜单管理', '#', 'menu', 'system/menu/index', '0', '1', 'C', 3, NULL, 'system:menu:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单管理菜单'),
    (300, 2, '部门管理', '#', 'dept', 'system/dept/index', '0', '1', 'C', 4, NULL, 'system:dept:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门管理菜单'),
    (301, 2, '岗位管理', '#', 'post', 'system/post/index', '0', '1', 'C', 5, NULL, 'system:post:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位管理菜单'),
    (302, 2, '字典管理', '#', 'dict', 'system/dict/index', '0', '1', 'C', 6, NULL, 'system:dict:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典管理菜单'),

    (310, 3, '用户列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:user:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户列表权限'),
    (6, 3, '用户新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:user:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户新增权限'),
    (7, 3, '用户查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:user:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户查询权限'),
    (8, 3, '用户编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:user:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户编辑权限'),
    (9, 3, '用户重置密码', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:user:resetPwd', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户重置密码权限'),
    (311, 3, '用户删除', NULL, NULL, NULL, '0', '0', 'F', 6, NULL, 'system:user:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户删除权限'),

    (10, 4, '角色列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:role:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色列表权限'),
    (11, 4, '角色新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:role:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色新增权限'),
    (12, 4, '角色查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:role:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色查询权限'),
    (13, 4, '角色编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:role:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色编辑权限'),
    (14, 4, '角色删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:role:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色删除权限'),

    (15, 5, '菜单列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:menu:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单列表权限'),
    (16, 5, '菜单新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:menu:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单新增权限'),
    (17, 5, '菜单查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:menu:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单查询权限'),
    (18, 5, '菜单编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:menu:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单编辑权限'),
    (19, 5, '菜单删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:menu:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单删除权限'),

    (320, 300, '部门列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:dept:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门列表权限'),
    (321, 300, '部门查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:dept:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门查询权限'),
    (322, 300, '部门新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:dept:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门新增权限'),
    (323, 300, '部门编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:dept:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门编辑权限'),
    (324, 300, '部门删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:dept:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门删除权限'),

    (330, 301, '岗位列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:post:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位列表权限'),
    (331, 301, '岗位查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:post:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位查询权限'),
    (332, 301, '岗位新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:post:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位新增权限'),
    (333, 301, '岗位编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:post:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位编辑权限'),
    (334, 301, '岗位删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:post:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位删除权限'),

    (340, 302, '字典列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:dict:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典列表权限'),
    (341, 302, '字典查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:dict:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典查询权限'),
    (342, 302, '字典新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:dict:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典新增权限'),
    (343, 302, '字典编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:dict:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典编辑权限'),
    (344, 302, '字典删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:dict:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典删除权限'),

    (200, NULL, '系统监控', '#', 'monitor', NULL, '0', '1', 'C', 20, NULL, 'monitor', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统监控目录'),
    (201, 200, '日志管理', '#', 'logs', 'monitor/log/index', '0', '1', 'C', 1, NULL, 'monitor:log:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志管理菜单'),
    (202, 200, '在线用户', '#', 'online', 'monitor/online/index', '0', '1', 'C', 2, NULL, 'monitor:online:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户菜单'),
    (203, 201, '登录日志查询', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:login:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '登录日志查询权限'),
    (204, 201, '操作日志查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:operation:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '操作日志查询权限'),
    (205, 201, '异常日志查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'monitor:exception:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '异常日志查询权限'),
    (206, 201, '日志删除', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'monitor:log:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志删除权限'),
    (207, 202, '在线用户查询', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:online:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户查询权限'),
    (208, 202, '强制下线', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:online:forceLogout', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '强制下线权限');

INSERT IGNORE INTO permissions (
    id, name, code, module, permission_type, api_path, api_method,
    status, create_time, update_time, remark
) VALUES
    (1, '用户新增', 'system:user:add', 'system', 'button', '/user/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户新增权限'),
    (2, '用户查询', 'system:user:query', 'system', 'button', '/user/{user_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户查询权限'),
    (3, '用户编辑', 'system:user:edit', 'system', 'button', '/user/{user_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户编辑权限'),
    (4, '用户重置密码', 'system:user:resetPwd', 'system', 'button', '/user/{user_id}/reset-password', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户重置密码权限'),
    (5, '角色列表', 'system:role:list', 'system', 'button', '/role/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色列表权限'),
    (6, '角色新增', 'system:role:add', 'system', 'button', '/role/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色新增权限'),
    (7, '角色查询', 'system:role:query', 'system', 'button', '/role/{role_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色查询权限'),
    (8, '角色编辑', 'system:role:edit', 'system', 'button', '/role/{role_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色编辑权限'),
    (9, '角色删除', 'system:role:remove', 'system', 'button', '/role/{role_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色删除权限'),
    (10, '菜单列表', 'system:menu:list', 'system', 'button', '/menu/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单列表权限'),
    (11, '菜单新增', 'system:menu:add', 'system', 'button', '/menu/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单新增权限'),
    (12, '超级管理员', '*:*:*', 'system', 'button', NULL, NULL, '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '超级管理员通配权限'),
    (13, '菜单查询', 'system:menu:query', 'system', 'button', '/menu/{menu_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单查询权限'),
    (14, '菜单编辑', 'system:menu:edit', 'system', 'button', '/menu/{menu_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单编辑权限'),
    (15, '菜单删除', 'system:menu:remove', 'system', 'button', '/menu/{menu_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单删除权限'),
    (310, '用户列表', 'system:user:list', 'system', 'button', '/user/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户列表权限'),
    (311, '用户删除', 'system:user:remove', 'system', 'button', '/user/{user_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户删除权限'),

    (320, '部门列表', 'system:dept:list', 'system', 'button', '/dept/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门列表权限'),
    (321, '部门查询', 'system:dept:query', 'system', 'button', '/dept/{dept_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门查询权限'),
    (322, '部门新增', 'system:dept:add', 'system', 'button', '/dept/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门新增权限'),
    (323, '部门编辑', 'system:dept:edit', 'system', 'button', '/dept/{dept_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门编辑权限'),
    (324, '部门删除', 'system:dept:remove', 'system', 'button', '/dept/{dept_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门删除权限'),

    (330, '岗位列表', 'system:post:list', 'system', 'button', '/post/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位列表权限'),
    (331, '岗位查询', 'system:post:query', 'system', 'button', '/post/{post_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位查询权限'),
    (332, '岗位新增', 'system:post:add', 'system', 'button', '/post/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位新增权限'),
    (333, '岗位编辑', 'system:post:edit', 'system', 'button', '/post/{post_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位编辑权限'),
    (334, '岗位删除', 'system:post:remove', 'system', 'button', '/post/{post_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位删除权限'),

    (340, '字典列表', 'system:dict:list', 'system', 'button', '/dict/type/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典列表权限'),
    (341, '字典查询', 'system:dict:query', 'system', 'button', '/dict/type/{dict_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典查询权限'),
    (342, '字典新增', 'system:dict:add', 'system', 'button', '/dict/type/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典新增权限'),
    (343, '字典编辑', 'system:dict:edit', 'system', 'button', '/dict/type/{dict_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典编辑权限'),
    (344, '字典删除', 'system:dict:remove', 'system', 'button', '/dict/type/{dict_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典删除权限'),

    (200, '登录日志查询', 'monitor:login:list', 'monitor', 'button', '/log/login/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '登录日志查询权限'),
    (201, '操作日志查询', 'monitor:operation:list', 'monitor', 'button', '/log/operation/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '操作日志查询权限'),
    (202, '异常日志查询', 'monitor:exception:list', 'monitor', 'button', '/log/exception/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '异常日志查询权限'),
    (203, '日志删除', 'monitor:log:remove', 'monitor', 'button', '/log/{log_type}/batch', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志删除权限'),
    (204, '在线用户查询', 'monitor:online:list', 'monitor', 'button', '/online/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户查询权限'),
    (205, '强制下线', 'monitor:online:forceLogout', 'monitor', 'button', '/online/token/{token_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '强制下线权限');

-- Keep existing permission metadata aligned when the endpoint path changes.
UPDATE permissions
SET api_path = '/user/{user_id}/reset-password',
    api_method = 'PUT',
    update_time = CURRENT_TIMESTAMP
WHERE code = 'system:user:resetPwd';

-- The built-in administrator role receives every built-in menu and button.
INSERT IGNORE INTO role_menu (role_id, menu_id)
SELECT 1, menu_id
FROM menu
WHERE menu_id IN (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    300, 301, 302, 310, 311,
    320, 321, 322, 323, 324,
    330, 331, 332, 333, 334,
    340, 341, 342, 343, 344,
    200, 201, 202, 203, 204, 205, 206, 207, 208
);

-- ---------------------------------------------------------------------------
-- 4. Dictionary reference data
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO dict_types (
    dict_id, dict_name, dict_type, status, remark, create_time, update_time
) VALUES
    (100, '用户性别', 'sys_user_sex', '1', '用户性别列表', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (101, '通用状态', 'sys_normal_disable', '1', '正常和停用状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (102, '是否选项', 'sys_yes_no', '1', '通用是否选项', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT IGNORE INTO dict_data (
    dict_code, dict_sort, dict_label, dict_value, dict_type,
    status, remark, create_time, update_time
) VALUES
    (1000, 1, '女', '0', 'sys_user_sex', '1', '性别女', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1001, 2, '男', '1', 'sys_user_sex', '1', '性别男', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1002, 3, '未知', '2', 'sys_user_sex', '1', '性别未知', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1010, 1, '正常', '1', 'sys_normal_disable', '1', '正常状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1011, 2, '停用', '0', 'sys_normal_disable', '1', '停用状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1020, 1, '是', '1', 'sys_yes_no', '1', '是', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (1021, 2, '否', '0', 'sys_yes_no', '1', '否', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
