import request from '@/utils/http'

// 获取统计数据
export function fetchGetStatisticsOverview() {
  return request.get({
    url: '/api/v1/admin/statistics/overview'
  })
}

export function fetchDetail() {
  return request.get({
    url: '/api/v1/admin/statistics/detail'
  })
}
