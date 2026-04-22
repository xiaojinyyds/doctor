/**
 * namespace: Api
 *
 * 所有接口相关类型定义
 * 在.vue文件使用会报错，需要在 eslint.config.mjs 中配置 globals: { Api: 'readonly' }
 */

declare namespace Api {
  /** 通用类型 */
  namespace Common {
    /** 分页参数 */
    interface PaginationParams {
      /** 当前页码 */
      current: number
      /** 每页条数 */
      size: number
      /** 总条数 */
      total: number
    }

    /** 通用搜索参数 */
    type CommonSearchParams = Pick<PaginationParams, 'current' | 'size'>

    /** 分页响应基础结构 */
    interface PaginatedResponse<T = any> {
      records: T[]
      current: number
      size: number
      total: number
    }

    /** 启用状态 */
    type EnableStatus = '1' | '2'
  }

  /** 认证类型 */
  namespace Auth {
    /** 登录参数 */
    interface LoginParams {
      account: string
      password: string
    }

    /** 注册参数 */
    interface RegisterParams {
      email: string
      phone: string
      code: string
      password: string
      /** 昵称/账号 */
      nickname: string
    }

    /** 发送验证码参数（邮箱验证码） */
    interface SendCodeParams {
      email: string
    }

    /** 登录响应 */
    interface LoginResponse {
      token: string
      refreshToken: string
    }

    /** 用户信息（B2B升级） */
    interface UserInfo {
      buttons: string[]
      roles: string[]
      userId: number
      userName: string
      email: string
      avatar?: string
      /** B2B升级：租户ID */
      tenantId?: string
      /** B2B升级：角色 */
      role?: 'user' | 'doctor' | 'admin'
      /** B2B升级：科室 */
      department?: string
      /** B2B升级：职称 */
      title?: string
      /** B2B升级：工号 */
      employeeId?: string
    }
  }

  /** 系统管理类型 */
  namespace SystemManage {
    /** 用户列表 */
    type UserList = Api.Common.PaginatedResponse<UserListItem>

    /** 用户列表项 */
    interface UserListItem {
      id: string
      nickname: string
      email: string
      status: string
      role: string
      created_at: string
      // 可选的其他字段
      avatar?: string
      phone?: string
      gender?: string
      updated_at?: string
    }

    /** 用户搜索参数 */
    interface UserSearchParams {
      /** 页码 */
      page?: number
      /** 每页数量 */
      size?: number
      /** 搜索关键词（邮箱/手机/昵称） */
      keyword?: string
      /** 角色筛选 */
      role?: string
      /** 状态筛选 */
      status?: string
    }

    /** 角色列表 */
    type RoleList = Api.Common.PaginatedResponse<RoleListItem>

    /** 角色列表项 */
    interface RoleListItem {
      roleId: number
      roleName: string
      roleCode: string
      description: string
      enabled: boolean
      createTime: string
    }

    /** 角色搜索参数 */
    type RoleSearchParams = Partial<
      Pick<RoleListItem, 'roleId' | 'roleName' | 'roleCode' | 'description' | 'enabled'> &
        Api.Common.CommonSearchParams
    >
  }

  /** 风险评估类型（V2.0） */
  namespace Assessment {
    /** V2.0 评估响应 */
    interface AssessmentV2Response {
      assessment_id: string
      questionnaire_id: string
      report_id: string
      assessment_result: {
        overall_risk: {
          score: number
          level: string
          percentile: number
        }
        category_risks: Record<
          string,
          {
            score: number
            level: string
          }
        >
        key_factors: Array<{
          factor: string
          contribution: number
          direction: 'increase' | 'decrease'
          description: string
          importance: number
        }>
        recommendations: Array<{
          category: string
          title: string
          content: string
          priority: number
          icon?: string
        }>
        ai_recommendation: string
      }
      user_profile: {
        age: number
        gender: string
        bmi: number
        smoking_status: number
        exercise_level: number
        stress_level: string
      }
      feature_importance: Array<{
        factor: string
        contribution: number
      }>
      shap_analysis: {
        values: number[]
        feature_values: Record<string, number>
      }
      model_info: {
        version: string
        feature_count: number
        inference_time_ms: number
        accuracy: number
        auc: number
      }
      created_at: string
    }

    /** 评估历史记录项 */
    interface AssessmentHistoryItem {
      id: string
      user_id: string
      questionnaire_id: string
      overall_risk_score: number
      overall_risk_level: string
      model_version: string
      created_at: string
      age: number
      gender: string
      share_info?: {
        share_token: string
        is_expired: boolean
        expire_at: string
      }
    }

    /** 评估历史列表响应 */
    interface AssessmentHistoryResponse {
      records: AssessmentHistoryItem[]
      total: number
      page: number
      page_size: number
    }
  }
}
