/**
 * 医生工作台API（B2B升级新增）
 */
import request from '@/utils/http'

/**
 * 获取待审核评估列表
 */
export function fetchPendingAssessments(params: {
  page?: number
  page_size?: number
  risk_level?: string
}) {
  return request.get<any>({
    url: '/api/v1/doctor/pending-assessments',
    params
  })
}

/**
 * 获取评估详情
 */
export function fetchAssessmentDetail(assessmentId: string) {
  return request.get<any>({
    url: `/api/v1/doctor/assessments/${assessmentId}`
  })
}

/**
 * 审核通过
 */
export function approveAssessment(assessmentId: string, data: {
  doctor_comment?: string
  doctor_risk_level?: string
}) {
  return request.post<any>({
    url: `/api/v1/doctor/assessments/${assessmentId}/approve`,
    data,
    showSuccessMessage: true
  })
}

/**
 * 驳回评估
 */
export function rejectAssessment(assessmentId: string, data: {
  reason: string
}) {
  return request.post<any>({
    url: `/api/v1/doctor/assessments/${assessmentId}/reject`,
    data,
    showSuccessMessage: true
  })
}

/**
 * 获取医生工作台统计
 */
export function fetchDoctorStatistics() {
  return request.get<any>({
    url: '/api/v1/doctor/statistics'
  })
}
