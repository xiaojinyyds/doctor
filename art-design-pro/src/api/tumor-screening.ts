/**
 * 肿瘤筛查系统API接口
 */
import http from '@/utils/http'

/**
 * 问卷相关接口
 */
export const questionnaireAPI = {
  // 提交问卷
  submit: (data: any) => {
    return http.post({
      url: '/questionnaire/submit',
      data
    })
  },

  // 获取问卷详情
  getById: (id: string) => {
    return http.get({
      url: `/questionnaire/${id}`
    })
  }
}

/**
 * 风险评估接口
 */
export const assessmentAPI = {
  // 评估风险
  evaluate: (questionnaireId: string) => {
    return http.post({
      url: `/assessment/evaluate/${questionnaireId}`
    })
  },

  // 获取评估结果
  getById: (id: string) => {
    return http.get({
      url: `/assessment/${id}`
    })
  },

  // 获取用户所有评估记录
  getUserAssessments: (params?: any) => {
    return http.get({
      url: '/assessment/user/list',
      params
    })
  }
}

/**
 * 报告相关接口
 */
export const reportAPI = {
  // 获取报告详情
  getById: (id: string) => {
    return http.get({
      url: `/report/${id}`
    })
  },

  // 导出PDF
  exportPDF: (id: string) => {
    return http.post({
      url: `/report/${id}/export`,
      data: {},
      responseType: 'blob'
    })
  },

  // 生成分享链接
  createShare: (id: string, data: any) => {
    return http.post({
      url: `/report/${id}/share`,
      data
    })
  }
}

/**
 * 历史记录接口
 */
export const historyAPI = {
  // 获取历史记录列表
  getList: (params?: any) => {
    return http.get({
      url: '/history/list',
      params
    })
  },

  // 对比分析
  compare: (id1: string, id2: string) => {
    return http.get({
      url: '/history/compare',
      params: { id1, id2 }
    })
  }
}

/**
 * 管理后台接口
 */
export const adminAPI = {
  // 获取所有用户
  getUsers: (params?: any) => {
    return http.get({
      url: '/admin/users',
      params
    })
  },

  // 获取所有筛查记录
  getAssessments: (params?: any) => {
    return http.get({
      url: '/admin/assessments',
      params
    })
  },

  // 获取统计数据
  getStatistics: () => {
    return http.get({
      url: '/admin/statistics'
    })
  },

  // 禁用/启用用户
  toggleUserStatus: (userId: string, status: string) => {
    return http.put({
      url: `/admin/user/${userId}/status`,
      data: { status }
    })
  }
}

