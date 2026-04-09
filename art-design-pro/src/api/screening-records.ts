import request from '@/utils/http'

// 获取筛查记录列表
export function fetchGetScreeningRecords(params: any) {
  return request.get({
    url: '/api/v1/admin/assessments',
    params
  })
}

// 删除筛查记录
export function fetchDeleteScreeningRecord(id: string) {
  return request.del({
    url: `/api/v1/admin/assessments/${id}`
  })
}

// 导出筛查记录
export function fetchScreeningRecord(id: string) {
  return request.get({
    url: `/api/v1/admin/assessments/${id}`
  })
}
