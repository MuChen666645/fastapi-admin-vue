-- FastAPI Admin 内置种子数据。
-- 执行前必须先完成 Alembic 迁移；本脚本不创建或修改数据库结构。
--
-- 设计约束：
-- 1. 所有内置记录使用固定业务 ID，保证菜单树和旧库迁移稳定。
-- 2. INSERT IGNORE 只负责补齐缺失记录，不覆盖已有业务字段。
-- 3. 旧数据修复只针对本脚本声明的内置记录，避免迁移其他租户的数据。

SET NAMES utf8mb4;
SET time_zone = '+08:00';

SET @seed_tenant_id := 1;
SET @seed_admin_role_code := 'admin';
SET @seed_common_role_code := 'common';

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- 1. 默认租户、角色、组织和岗位
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO tenants (
    id, code, name, description, status, version, create_time, update_time
) VALUES
    (@seed_tenant_id, 'default', '默认租户', '系统内置默认租户', '1', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 早期数据库可能已经存在默认租户，但缺少生命周期字段的有效状态。
UPDATE tenants
SET status = '1', deleted_at = NULL, update_time = CURRENT_TIMESTAMP
WHERE id = @seed_tenant_id
  AND code = 'default'
  AND (status <> '1' OR deleted_at IS NOT NULL);

INSERT IGNORE INTO roles (
    id, name, code, tenant_id, description, create_time, update_time, status,
    version, data_scope
) VALUES
    (1, '超级管理员', @seed_admin_role_code, @seed_tenant_id, '系统内置超级管理员角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '1', 1, '1'),
    (2, '普通管理员', @seed_common_role_code, @seed_tenant_id, '系统内置普通管理员角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '1', 1, '5');

INSERT IGNORE INTO departments (
    tenant_id, dept_id, parent_id, ancestors, dept_name, order_num, leader,
    phone, email, status, create_time, update_time
) VALUES
    (@seed_tenant_id, 100, NULL, '0', '集团总部', 0, '管理员', '13800000000', 'admin@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 101, 100, '0,100', '研发中心', 1, '研发负责人', '13800000001', 'rd@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 102, 101, '0,100,101', '前端研发部', 1, '前端负责人', '13800000002', 'frontend@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 103, 101, '0,100,101', '后端研发部', 2, '后端负责人', '13800000003', 'backend@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 104, 100, '0,100', '运维部', 2, '运维负责人', '13800000004', 'ops@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 105, 100, '0,100', '财务部', 3, '财务负责人', '13800000005', 'finance@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 106, 100, '0,100', '人力资源部', 4, '人事负责人', '13800000006', 'hr@example.com', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT IGNORE INTO posts (
    tenant_id, post_id, post_code, post_name, post_sort, status, remark,
    create_time, update_time
) VALUES
    (@seed_tenant_id, 100, 'general_manager', '总经理', 1, '1', '公司负责人', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 101, 'developer', '研发工程师', 2, '1', '产品研发岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 102, 'test_engineer', '测试工程师', 3, '1', '质量保障岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 103, 'operations', '运维工程师', 4, '1', '系统运维岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 104, 'finance', '财务专员', 5, '1', '财务管理岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 105, 'human_resources', '人事专员', 6, '1', '人力资源岗位', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 仅修复早期种子没有写入的租户归属，不移动已经属于其他租户的记录。
UPDATE roles
SET tenant_id = @seed_tenant_id, update_time = CURRENT_TIMESTAMP
WHERE code IN (@seed_admin_role_code, @seed_common_role_code)
  AND tenant_id IS NULL;

UPDATE departments
SET tenant_id = @seed_tenant_id
WHERE dept_id BETWEEN 100 AND 106
  AND tenant_id IS NULL;

UPDATE posts
SET tenant_id = @seed_tenant_id
WHERE post_id BETWEEN 100 AND 105
  AND tenant_id IS NULL;

-- ---------------------------------------------------------------------------
-- 2. 内置用户和租户、角色、岗位关系
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO users (
    id, create_time, username, password, email, phone, role_id, tenant_id, dept_id,
    nickname, sex, avatar, update_time, status, password_changed_at,
    must_change_password, version, auth_provider
) VALUES
    (1, CURRENT_TIMESTAMP, 'admin', '$5$rounds=535000$ZOQUh73DBElH3Hff$BpUOeegYosS8Y0VbHqFM.fNAxdyBUN1yHUcUKWJUSx6', 'fastapi-admin@136.com', '13688888888', 1, @seed_tenant_id, 100, 'fastapi-admin', '1', '', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP, 0, 1, 'local'),
    (2, CURRENT_TIMESTAMP, 'test', '$5$rounds=535000$ZOQUh73DBElH3Hff$BpUOeegYosS8Y0VbHqFM.fNAxdyBUN1yHUcUKWJUSx6', 'fastapi-test@136.com', '13588888888', 2, @seed_tenant_id, 101, 'fastapi-user', '1', '', CURRENT_TIMESTAMP, '1', CURRENT_TIMESTAMP, 0, 1, 'local');

-- 兼容早期没有 tenant_id 或 role_id 的 admin/test 记录。
-- tenant_id 非空且属于其他租户时不强行搬迁，避免覆盖业务归属。
UPDATE users AS u
JOIN roles AS r
  ON r.code = CASE u.username
      WHEN 'admin' THEN @seed_admin_role_code
      ELSE @seed_common_role_code
    END
 AND r.tenant_id = @seed_tenant_id
SET u.tenant_id = @seed_tenant_id,
    u.role_id = r.id
WHERE u.username IN ('admin', 'test')
  AND (u.tenant_id IS NULL OR u.tenant_id = @seed_tenant_id)
  AND (u.tenant_id IS NULL OR u.role_id IS NULL OR u.role_id <> r.id);

INSERT IGNORE INTO tenant_members (
    user_id, tenant_id, status, is_default, version, joined_at, updated_at
)
SELECT u.id, @seed_tenant_id, u.status, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM users AS u
WHERE u.username IN ('admin', 'test')
  AND u.tenant_id = @seed_tenant_id;

-- 内置账号必须保持默认租户成员关系有效，否则登录会在密码和 MFA 校验前失败。
UPDATE tenant_members AS tm
JOIN users AS u ON u.id = tm.user_id
SET tm.status = u.status,
    tm.is_default = TRUE,
    tm.deleted_at = NULL,
    tm.version = tm.version + 1,
    tm.updated_at = CURRENT_TIMESTAMP
WHERE u.username IN ('admin', 'test')
  AND u.tenant_id = @seed_tenant_id
  AND tm.tenant_id = @seed_tenant_id
  AND (
      tm.status <> u.status
      OR tm.is_default = FALSE
      OR tm.deleted_at IS NOT NULL
  );

INSERT IGNORE INTO user_role (tenant_id, user_id, role_id)
SELECT @seed_tenant_id, u.id, r.id
FROM users AS u
JOIN roles AS r
  ON r.code = CASE u.username
      WHEN 'admin' THEN @seed_admin_role_code
      ELSE @seed_common_role_code
    END
 AND r.tenant_id = @seed_tenant_id
WHERE u.username IN ('admin', 'test')
  AND u.tenant_id = @seed_tenant_id;

INSERT IGNORE INTO user_post (tenant_id, user_id, post_id)
SELECT @seed_tenant_id, u.id, p.post_id
FROM users AS u
JOIN posts AS p
  ON p.post_code = CASE u.username
      WHEN 'admin' THEN 'general_manager'
      ELSE 'developer'
    END
 AND p.tenant_id = @seed_tenant_id
WHERE u.username IN ('admin', 'test')
  AND u.tenant_id = @seed_tenant_id;

-- ---------------------------------------------------------------------------
-- 3. 消息中心种子
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO messages (
    id, tenant_id, message_title, message_type, message_content, status,
    publish_time, create_by, create_time, update_time
) VALUES
    (400, @seed_tenant_id, '平台服务升级', 'system', '平台将进行例行服务升级，请提前保存正在编辑的内容。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (401, @seed_tenant_id, '系统安全策略更新', 'system', '系统安全策略已更新，请按照最新要求完成账号安全设置。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (402, @seed_tenant_id, '数据备份完成', 'system', '本次系统数据备份已完成，备份任务运行正常。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (403, @seed_tenant_id, '平台功能更新', 'system', '消息中心已支持系统通知、审批消息和报警提醒三类消息。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (404, @seed_tenant_id, '欢迎使用管理平台', 'system', '欢迎使用 FastAPI Admin 管理平台。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (405, @seed_tenant_id, '采购申请待审批', 'approval', '有新的采购申请等待审批，请及时处理。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (406, @seed_tenant_id, '报销申请待审批', 'approval', '有新的报销申请等待审批，请及时处理。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (407, @seed_tenant_id, '请假申请待审批', 'approval', '有新的请假申请等待审批，请及时处理。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (408, @seed_tenant_id, '合同申请待审批', 'approval', '有新的合同申请等待审批，请及时处理。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (409, @seed_tenant_id, '用章申请待审批', 'approval', '有新的用章申请等待审批，请及时处理。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (410, @seed_tenant_id, '接口响应时间异常', 'alarm', '检测到接口响应时间异常，请检查相关服务运行状态。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (411, @seed_tenant_id, '磁盘空间不足', 'alarm', '检测到服务器磁盘空间不足，请及时清理或扩容。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (412, @seed_tenant_id, '任务执行失败', 'alarm', '检测到定时任务执行失败，请查看任务日志。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (413, @seed_tenant_id, 'Redis 连接异常', 'alarm', '检测到 Redis 连接异常，请检查基础设施和网络状态。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (414, @seed_tenant_id, '数据库连接池预警', 'alarm', '检测到数据库连接池使用率较高，请关注服务负载。', '1', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ---------------------------------------------------------------------------
-- 4. 权限目录
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO permissions (
    name, code, module, permission_type, api_path, api_method,
    status, create_time, update_time, remark
) VALUES
    ('用户新增', 'system:user:add', 'system', 'button', '/user/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户新增权限'),
    ('用户查询', 'system:user:query', 'system', 'button', '/user/{user_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户查询权限'),
    ('用户编辑', 'system:user:edit', 'system', 'button', '/user/{user_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户编辑权限'),
    ('用户重置密码', 'system:user:resetPwd', 'system', 'button', '/user/{user_id}/reset-password', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户重置密码权限'),
    ('角色列表', 'system:role:list', 'system', 'button', '/role/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色列表权限'),
    ('角色新增', 'system:role:add', 'system', 'button', '/role/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色新增权限'),
    ('角色查询', 'system:role:query', 'system', 'button', '/role/{role_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色查询权限'),
    ('角色编辑', 'system:role:edit', 'system', 'button', '/role/{role_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色编辑权限'),
    ('角色删除', 'system:role:remove', 'system', 'button', '/role/{role_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色删除权限'),
    ('菜单列表', 'system:menu:list', 'system', 'button', '/menu/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单列表权限'),
    ('菜单新增', 'system:menu:add', 'system', 'button', '/menu/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单新增权限'),
    ('超级管理员', '*:*:*', 'system', 'button', NULL, NULL, '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '超级管理员通配权限'),
    ('菜单查询', 'system:menu:query', 'system', 'button', '/menu/{menu_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单查询权限'),
    ('菜单编辑', 'system:menu:edit', 'system', 'button', '/menu/{menu_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单编辑权限'),
    ('菜单删除', 'system:menu:remove', 'system', 'button', '/menu/{menu_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单删除权限'),
    ('用户列表', 'system:user:list', 'system', 'button', '/user/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户列表权限'),
    ('用户删除', 'system:user:remove', 'system', 'button', '/user/{user_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户删除权限'),
    ('部门列表', 'system:dept:list', 'system', 'button', '/dept/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门列表权限'),
    ('部门查询', 'system:dept:query', 'system', 'button', '/dept/{dept_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门查询权限'),
    ('部门新增', 'system:dept:add', 'system', 'button', '/dept/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门新增权限'),
    ('部门编辑', 'system:dept:edit', 'system', 'button', '/dept/{dept_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门编辑权限'),
    ('部门删除', 'system:dept:remove', 'system', 'button', '/dept/{dept_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门删除权限'),
    ('岗位列表', 'system:post:list', 'system', 'button', '/post/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位列表权限'),
    ('岗位查询', 'system:post:query', 'system', 'button', '/post/{post_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位查询权限'),
    ('岗位新增', 'system:post:add', 'system', 'button', '/post/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位新增权限'),
    ('岗位编辑', 'system:post:edit', 'system', 'button', '/post/{post_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位编辑权限'),
    ('岗位删除', 'system:post:remove', 'system', 'button', '/post/{post_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位删除权限'),
    ('字典列表', 'system:dict:list', 'system', 'button', '/dict/type/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典列表权限'),
    ('字典查询', 'system:dict:query', 'system', 'button', '/dict/type/{dict_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典查询权限'),
    ('字典新增', 'system:dict:add', 'system', 'button', '/dict/type/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典新增权限'),
    ('字典编辑', 'system:dict:edit', 'system', 'button', '/dict/type/{dict_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典编辑权限'),
    ('字典删除', 'system:dict:remove', 'system', 'button', '/dict/type/{dict_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典删除权限'),
    ('登录日志查询', 'monitor:login:list', 'monitor', 'button', '/log/login/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '登录日志查询权限'),
    ('操作日志查询', 'monitor:operation:list', 'monitor', 'button', '/log/operation/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '操作日志查询权限'),
    ('异常日志查询', 'monitor:exception:list', 'monitor', 'button', '/log/exception/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '异常日志查询权限'),
    ('日志删除', 'monitor:log:remove', 'monitor', 'button', '/log/{log_type}/batch', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志删除权限'),
    ('在线用户查询', 'monitor:online:list', 'monitor', 'button', '/online/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户查询权限'),
    ('强制下线', 'monitor:online:forceLogout', 'monitor', 'button', '/online/token/{token_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '强制下线权限'),
    ('用户邮箱字段', 'field:user:email', 'user', 'field', NULL, NULL, '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '查看用户邮箱字段'),
    ('用户手机号字段', 'field:user:phone', 'user', 'field', NULL, NULL, '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '查看用户手机号字段'),
    ('用户头像字段', 'field:user:avatar', 'user', 'field', NULL, NULL, '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '查看用户头像字段'),
    ('文件上传', 'system:file:upload', 'system', 'button', '/file/upload', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '文件上传权限'),
    ('文件下载', 'system:file:download', 'system', 'button', '/file/download/{file_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '文件下载权限'),
    ('文件删除', 'system:file:remove', 'system', 'button', '/file/{file_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '文件删除权限'),
    ('配置列表', 'system:config:list', 'system', 'button', '/config/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统配置列表权限'),
    ('配置查询', 'system:config:query', 'system', 'button', '/config/{config_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统配置查询权限'),
    ('配置新增', 'system:config:add', 'system', 'button', '/config/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统配置新增权限'),
    ('配置编辑', 'system:config:edit', 'system', 'button', '/config/{config_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统配置编辑权限'),
    ('配置删除', 'system:config:remove', 'system', 'button', '/config/{config_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统配置删除权限'),
    ('消息列表', 'system:message:list', 'system', 'button', '/message/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息列表权限'),
    ('消息查询', 'system:message:query', 'system', 'button', '/message/{message_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息查询权限'),
    ('消息新增', 'system:message:add', 'system', 'button', '/message/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息新增权限'),
    ('消息编辑', 'system:message:edit', 'system', 'button', '/message/{message_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息编辑权限'),
    ('消息删除', 'system:message:remove', 'system', 'button', '/message/{message_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息删除权限'),
    ('任务列表', 'monitor:job:list', 'monitor', 'button', '/job/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务列表权限'),
    ('任务查询', 'monitor:job:query', 'monitor', 'button', '/job/{job_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务查询权限'),
    ('任务新增', 'monitor:job:add', 'monitor', 'button', '/job/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务新增权限'),
    ('任务编辑', 'monitor:job:edit', 'monitor', 'button', '/job/{job_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务编辑权限'),
    ('任务删除', 'monitor:job:remove', 'monitor', 'button', '/job/{job_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务删除权限'),
    ('任务执行', 'monitor:job:run', 'monitor', 'button', '/job/{job_id}/run', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务执行权限'),
    ('备份创建', 'system:backup:create', 'system', 'button', '/ops/backup/create', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '备份创建权限'),
    ('备份恢复', 'system:backup:restore', 'system', 'button', '/ops/backup/restore', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '备份恢复权限'),
    ('备份校验', 'system:backup:verify', 'system', 'button', '/ops/backup/verify', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '备份校验权限'),
    ('备份演练', 'system:backup:rehearse', 'system', 'button', '/ops/backup/rehearse', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '备份恢复演练权限'),
    ('租户列表', 'system:tenant:list', 'system', 'button', '/tenant/list/all', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户列表权限'),
    ('租户新增', 'system:tenant:add', 'system', 'button', '/tenant/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户新增权限'),
    ('租户编辑', 'system:tenant:edit', 'system', 'button', '/tenant/{tenant_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户编辑权限'),
    ('租户删除', 'system:tenant:remove', 'system', 'button', '/tenant/{tenant_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户删除权限'),
    ('租户成员列表', 'system:tenant:member:list', 'system', 'button', '/tenant/{tenant_id}/members', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员列表权限'),
    ('租户成员新增', 'system:tenant:member:add', 'system', 'button', '/tenant/{tenant_id}/members', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员新增权限'),
    ('租户成员编辑', 'system:tenant:member:edit', 'system', 'button', '/tenant/{tenant_id}/members/{user_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员编辑权限'),
    ('租户成员删除', 'system:tenant:member:remove', 'system', 'button', '/tenant/{tenant_id}/members/{user_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员删除权限'),
    ('密钥轮换', 'system:secret:rotate', 'system', 'button', '/ops/secrets/rotate', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '密钥轮换权限');

-- 迁移或旧版本可能写入了旧接口路径；只同步明确变更过的路径。
UPDATE permissions
SET api_path = '/user/{user_id}/reset-password',
    api_method = 'PUT',
    update_time = CURRENT_TIMESTAMP
WHERE code = 'system:user:resetPwd';

-- ---------------------------------------------------------------------------
-- 5. 菜单树和按钮菜单
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO menu (
    tenant_id, menu_id, parent_id, menu_name, icon, menu_path, component,
    is_hidden, is_cache, menu_type, sort, link_url, perms, status,
    create_time, update_time, remark
) VALUES
    (@seed_tenant_id, 1, NULL, '首页', 'HomeOutline', 'dashboard', 'home/index', '0', '1', 'C', 1, NULL, 'dashboard', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '首页菜单'),
    (@seed_tenant_id, 2, NULL, '系统管理', 'SettingsOutline', 'system', NULL, '0', '1', 'C', 10, NULL, 'system', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统管理目录'),
    (@seed_tenant_id, 200, NULL, '系统监控', 'AnalyticsOutline', 'monitor', NULL, '0', '1', 'C', 20, NULL, 'monitor', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统监控目录'),
    (@seed_tenant_id, 3, 2, '用户管理', 'PeopleOutline', 'user', 'system/user/index', '0', '1', 'C', 1, NULL, 'system:user:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户管理菜单'),
    (@seed_tenant_id, 4, 2, '角色管理', 'ShieldCheckmarkOutline', 'role', 'system/role/index', '0', '1', 'C', 2, NULL, 'system:role:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色管理菜单'),
    (@seed_tenant_id, 5, 2, '菜单管理', 'MenuOutline', 'menu', 'system/menu/index', '0', '1', 'C', 3, NULL, 'system:menu:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单管理菜单'),
    (@seed_tenant_id, 300, 2, '部门管理', 'BusinessOutline', 'dept', 'system/dept/index', '0', '1', 'C', 4, NULL, 'system:dept:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门管理菜单'),
    (@seed_tenant_id, 301, 2, '岗位管理', 'BriefcaseOutline', 'post', 'system/post/index', '0', '1', 'C', 5, NULL, 'system:post:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位管理菜单'),
    (@seed_tenant_id, 302, 2, '字典管理', 'BookOutline', 'dict', 'system/dict/index', '0', '1', 'C', 6, NULL, 'system:dict:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典管理菜单'),
    (@seed_tenant_id, 201, 200, '日志管理', 'DocumentTextOutline', 'logs', 'monitor/log/index', '0', '1', 'C', 1, NULL, 'monitor:log:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志管理菜单'),
    (@seed_tenant_id, 202, 200, '在线用户', 'GlobeOutline', 'online', 'monitor/online/index', '0', '1', 'C', 2, NULL, 'monitor:online:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户菜单'),
    (@seed_tenant_id, 351, 2, '系统参数', 'SettingsOutline', 'config', 'system/config/index', '0', '1', 'C', 8, NULL, 'system:config:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '系统参数管理菜单'),
    (@seed_tenant_id, 352, 2, '消息中心', 'NotificationsOutline', 'message', 'system/message/index', '0', '1', 'C', 9, NULL, 'system:message:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息中心'),
    (@seed_tenant_id, 353, 2, '租户管理', 'BusinessOutline', 'tenant', 'system/tenant/index', '0', '1', 'C', 10, NULL, 'system:tenant:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户管理菜单'),
    (@seed_tenant_id, 360, 200, '定时任务', 'TimeOutline', 'job', 'monitor/job/index', '0', '1', 'C', 3, NULL, 'monitor:job:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '定时任务'),
    (@seed_tenant_id, 310, 3, '用户列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:user:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户列表权限'),
    (@seed_tenant_id, 6, 3, '用户新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:user:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户新增权限'),
    (@seed_tenant_id, 7, 3, '用户查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:user:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户查询权限'),
    (@seed_tenant_id, 8, 3, '用户编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:user:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户编辑权限'),
    (@seed_tenant_id, 9, 3, '用户重置密码', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:user:resetPwd', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户重置密码权限'),
    (@seed_tenant_id, 311, 3, '用户删除', NULL, NULL, NULL, '0', '0', 'F', 6, NULL, 'system:user:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '用户删除权限'),
    (@seed_tenant_id, 10, 4, '角色列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:role:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色列表权限'),
    (@seed_tenant_id, 11, 4, '角色新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:role:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色新增权限'),
    (@seed_tenant_id, 12, 4, '角色查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:role:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色查询权限'),
    (@seed_tenant_id, 13, 4, '角色编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:role:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色编辑权限'),
    (@seed_tenant_id, 14, 4, '角色删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:role:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '角色删除权限'),
    (@seed_tenant_id, 15, 5, '菜单列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:menu:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单列表权限'),
    (@seed_tenant_id, 16, 5, '菜单新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:menu:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单新增权限'),
    (@seed_tenant_id, 17, 5, '菜单查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:menu:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单查询权限'),
    (@seed_tenant_id, 18, 5, '菜单编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:menu:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单编辑权限'),
    (@seed_tenant_id, 19, 5, '菜单删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:menu:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '菜单删除权限'),
    (@seed_tenant_id, 320, 300, '部门列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:dept:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门列表权限'),
    (@seed_tenant_id, 321, 300, '部门查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:dept:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门查询权限'),
    (@seed_tenant_id, 322, 300, '部门新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:dept:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门新增权限'),
    (@seed_tenant_id, 323, 300, '部门编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:dept:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门编辑权限'),
    (@seed_tenant_id, 324, 300, '部门删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:dept:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '部门删除权限'),
    (@seed_tenant_id, 330, 301, '岗位列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:post:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位列表权限'),
    (@seed_tenant_id, 331, 301, '岗位查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:post:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位查询权限'),
    (@seed_tenant_id, 332, 301, '岗位新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:post:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位新增权限'),
    (@seed_tenant_id, 333, 301, '岗位编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:post:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位编辑权限'),
    (@seed_tenant_id, 334, 301, '岗位删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:post:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '岗位删除权限'),
    (@seed_tenant_id, 340, 302, '字典列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:dict:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典列表权限'),
    (@seed_tenant_id, 341, 302, '字典查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:dict:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典查询权限'),
    (@seed_tenant_id, 342, 302, '字典新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:dict:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典新增权限'),
    (@seed_tenant_id, 343, 302, '字典编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:dict:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典编辑权限'),
    (@seed_tenant_id, 344, 302, '字典删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:dict:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '字典删除权限'),
    (@seed_tenant_id, 203, 201, '登录日志查询', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:login:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '登录日志查询权限'),
    (@seed_tenant_id, 204, 201, '操作日志查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:operation:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '操作日志查询权限'),
    (@seed_tenant_id, 205, 201, '异常日志查询', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'monitor:exception:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '异常日志查询权限'),
    (@seed_tenant_id, 206, 201, '日志删除', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'monitor:log:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '日志删除权限'),
    (@seed_tenant_id, 207, 202, '在线用户查询', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:online:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '在线用户查询权限'),
    (@seed_tenant_id, 208, 202, '强制下线', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:online:forceLogout', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '强制下线权限'),
    (@seed_tenant_id, 373, 351, '配置列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:config:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '配置列表权限'),
    (@seed_tenant_id, 374, 351, '配置查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:config:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '配置查询权限'),
    (@seed_tenant_id, 375, 351, '配置新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:config:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '配置新增权限'),
    (@seed_tenant_id, 376, 351, '配置编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:config:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '配置编辑权限'),
    (@seed_tenant_id, 377, 351, '配置删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:config:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '配置删除权限'),
    (@seed_tenant_id, 389, 353, '租户列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:tenant:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户列表权限'),
    (@seed_tenant_id, 390, 353, '租户新增', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:tenant:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户新增权限'),
    (@seed_tenant_id, 391, 353, '租户编辑', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:tenant:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户编辑权限'),
    (@seed_tenant_id, 392, 353, '租户删除', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:tenant:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户删除权限'),
    (@seed_tenant_id, 393, 353, '租户成员列表', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:tenant:member:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员列表权限'),
    (@seed_tenant_id, 394, 353, '租户成员新增', NULL, NULL, NULL, '0', '0', 'F', 6, NULL, 'system:tenant:member:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员新增权限'),
    (@seed_tenant_id, 395, 353, '租户成员编辑', NULL, NULL, NULL, '0', '0', 'F', 7, NULL, 'system:tenant:member:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员编辑权限'),
    (@seed_tenant_id, 396, 353, '租户成员删除', NULL, NULL, NULL, '0', '0', 'F', 8, NULL, 'system:tenant:member:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '租户成员删除权限'),
    (@seed_tenant_id, 378, 352, '消息列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:message:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息列表权限'),
    (@seed_tenant_id, 379, 352, '消息查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:message:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息查询权限'),
    (@seed_tenant_id, 380, 352, '消息新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:message:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息新增权限'),
    (@seed_tenant_id, 381, 352, '消息编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:message:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息编辑权限'),
    (@seed_tenant_id, 382, 352, '消息删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:message:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '消息删除权限'),
    (@seed_tenant_id, 383, 360, '任务列表', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:job:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务列表权限'),
    (@seed_tenant_id, 384, 360, '任务查询', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:job:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务查询权限'),
    (@seed_tenant_id, 385, 360, '任务新增', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'monitor:job:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务新增权限'),
    (@seed_tenant_id, 386, 360, '任务编辑', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'monitor:job:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务编辑权限'),
    (@seed_tenant_id, 387, 360, '任务删除', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'monitor:job:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务删除权限'),
    (@seed_tenant_id, 388, 360, '任务执行', NULL, NULL, NULL, '0', '0', 'F', 6, NULL, 'monitor:job:run', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '任务执行权限');

-- 兼容旧菜单记录没有 tenant_id 的情况；不触碰其他菜单。
UPDATE menu
SET tenant_id = @seed_tenant_id
WHERE tenant_id IS NULL
  AND (
      menu_id IN (
          1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
          200, 201, 202, 203, 204, 205, 206, 207, 208,
          300, 301, 302, 310, 311, 320, 321, 322, 323, 324,
          330, 331, 332, 333, 334, 340, 341, 342, 343, 344
      )
      OR menu_id IN (351, 352, 353, 360, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396)
  );

-- 同步内置路由菜单，兼容已存在但仍使用旧名称或旧组件路径的默认租户记录。
UPDATE menu
SET menu_name = '系统参数',
    menu_path = 'config',
    component = 'system/config/index',
    perms = 'system:config:list',
    status = '1',
    remark = '系统参数管理菜单',
    update_time = CURRENT_TIMESTAMP
WHERE tenant_id = @seed_tenant_id
  AND menu_id = 351;

UPDATE menu
SET parent_id = 2,
    menu_name = '租户管理',
    icon = 'BusinessOutline',
    menu_path = 'tenant',
    component = 'system/tenant/index',
    is_hidden = '0',
    is_cache = '1',
    menu_type = 'C',
    sort = 10,
    link_url = NULL,
    perms = 'system:tenant:list',
    status = '1',
    remark = '租户管理菜单',
    update_time = CURRENT_TIMESTAMP
WHERE tenant_id = @seed_tenant_id
  AND menu_id = 353;

-- 清理已移除的文件管理菜单及其角色菜单关联，保留文件 API 权限目录。
DELETE rm
FROM role_menu AS rm
INNER JOIN menu AS m ON m.menu_id = rm.menu_id
WHERE m.tenant_id = @seed_tenant_id
  AND m.menu_id IN (350, 370, 371, 372);

DELETE FROM menu
WHERE tenant_id = @seed_tenant_id
  AND menu_id IN (370, 371, 372);

DELETE FROM menu
WHERE tenant_id = @seed_tenant_id
  AND menu_id = 350;

-- 幂等同步内置路由菜单的 Ionicons5 图标；不覆盖按钮菜单或其他租户菜单。
UPDATE menu
SET icon = CASE menu_id
    WHEN 1 THEN 'HomeOutline'
    WHEN 2 THEN 'SettingsOutline'
    WHEN 200 THEN 'AnalyticsOutline'
    WHEN 3 THEN 'PeopleOutline'
    WHEN 4 THEN 'ShieldCheckmarkOutline'
    WHEN 5 THEN 'MenuOutline'
    WHEN 300 THEN 'BusinessOutline'
    WHEN 301 THEN 'BriefcaseOutline'
    WHEN 302 THEN 'BookOutline'
    WHEN 201 THEN 'DocumentTextOutline'
    WHEN 202 THEN 'GlobeOutline'
    WHEN 351 THEN 'SettingsOutline'
    WHEN 352 THEN 'NotificationsOutline'
    WHEN 353 THEN 'BusinessOutline'
    WHEN 360 THEN 'TimeOutline'
END
WHERE tenant_id = @seed_tenant_id
  AND menu_type = 'C'
  AND menu_id IN (1, 2, 3, 4, 5, 200, 201, 202, 300, 301, 302, 351, 352, 353, 360);

-- 超级管理员只补齐本脚本声明的内置菜单，不吸收其他租户的业务菜单。
INSERT IGNORE INTO role_menu (role_id, menu_id)
SELECT r.id, m.menu_id
FROM roles AS r
JOIN menu AS m
  ON m.tenant_id = @seed_tenant_id
 AND (
      m.menu_id IN (
          1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
          200, 201, 202, 203, 204, 205, 206, 207, 208,
          300, 301, 302, 310, 311, 320, 321, 322, 323, 324,
          330, 331, 332, 333, 334, 340, 341, 342, 343, 344
      )
      OR m.menu_id IN (351, 352, 353, 360, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396)
 )
WHERE r.code = @seed_admin_role_code
  AND r.tenant_id = @seed_tenant_id;

-- ---------------------------------------------------------------------------
-- 6. 字典数据
-- ---------------------------------------------------------------------------

INSERT IGNORE INTO dict_types (
    tenant_id, dict_id, dict_name, dict_type, status, remark, create_time, update_time
) VALUES
    (@seed_tenant_id, 100, '用户性别', 'sys_user_sex', '1', '用户性别列表', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 101, '通用状态', 'sys_normal_disable', '1', '正常和停用状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 102, '是否选项', 'sys_yes_no', '1', '通用是否选项', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT IGNORE INTO dict_data (
    tenant_id, dict_code, dict_sort, dict_label, dict_value, dict_type,
    status, remark, create_time, update_time
) VALUES
    (@seed_tenant_id, 1000, 1, '女', '0', 'sys_user_sex', '1', '性别女', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1001, 2, '男', '1', 'sys_user_sex', '1', '性别男', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1002, 3, '未知', '2', 'sys_user_sex', '1', '性别未知', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1010, 1, '正常', '1', 'sys_normal_disable', '1', '正常状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1011, 2, '停用', '0', 'sys_normal_disable', '1', '停用状态', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1020, 1, '是', '1', 'sys_yes_no', '1', '是', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (@seed_tenant_id, 1021, 2, '否', '0', 'sys_yes_no', '1', '否', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

UPDATE dict_types
SET tenant_id = @seed_tenant_id
WHERE dict_type IN ('sys_user_sex', 'sys_normal_disable', 'sys_yes_no')
  AND tenant_id IS NULL;

UPDATE dict_data
SET tenant_id = @seed_tenant_id
WHERE dict_type IN ('sys_user_sex', 'sys_normal_disable', 'sys_yes_no')
  AND tenant_id IS NULL;

COMMIT;
