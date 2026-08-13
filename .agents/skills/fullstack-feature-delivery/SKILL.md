---
name: fullstack-feature-delivery
description: 交付需要 Vue 管理端和 FastAPI 服务共同修改的业务功能，包括页面、菜单路由、权限、租户、DTO、Service、DAO、迁移、seed、后台任务与跨端回归测试时使用。
---

# 全栈功能交付

用于编排跨项目功能，具体实现分别遵循前端和后端领域 Skill。先确认功能确实需要双端变更，
不要因便利扩大单端任务。

## 工作流程

1. 记录用户路径、目标端、影响端、角色、租户、资源、状态变化和明确不在范围内的内容。
2. 读取 `fullstack-contract-change` 的契约要求，核对 service Controller/DTO/Service/DAO/迁移/seed
   与 frontend API/Parser/Store/Router/View/测试。
3. 后端先实现最终业务规则：认证、权限、租户、数据范围、事务、幂等、审计、任务和失败语义。
4. 前端再实现类型化调用、完整页面状态、权限可见性、Loading、禁用、错误、成功、重复提交和
   handler 防护；前端限制不能替代后端校验。
5. 菜单、路由和权限相关功能同步检查：后端菜单/权限 seed、前端动态路由白名单、静态路由守卫、
   标签、缓存和系统设置抽屉边界。
6. 涉及 schema 时新增迁移，不删除或重写已应用版本；同步模型、DAO、Service、初始化 SQL、
   权限 seed 与离线 SQL 测试。
7. 分别运行两端目标测试，再按改动扩大到构建、完整测试、离线迁移 SQL 和明确授权后的集成验证。

## 交付

说明两端文件、接口、权限、租户/状态、迁移、验证结果、未执行项和剩余风险。详细门禁见
[feature-delivery-checklist.md](references/feature-delivery-checklist.md)。
