import { AppRouteRecord } from '@/types/router'

/**
 * 风险报告路由
 * 注意：移除了 roles 限制，所有登录用户都可以访问
 */
export const reportRoutes: AppRouteRecord = {
  path: '/report',
  name: 'Report',
  component: '/index/index',
  meta: {
    title: '风险报告',
    icon: '&#xe721;', // 报告图标

    isHide: true
  },
  children: [
    {
      path: ':id',
      name: 'ReportDetail',
      component: '/report/index',
      meta: {
        title: '报告详情',
        keepAlive: false,
        isHideTab: true,
        isHide: true
      }
    }
  ]
}
