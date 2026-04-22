import { AppRouteRecord } from '@/types/router'

/**
 * 风险评估 路由
 * 所有用户都可访问
 */
export const riskRoutes: AppRouteRecord = {
  path: '/risk',
  name: 'Risk',
  component: '/risk/index',
  meta: {
    title: '风险评估',
    icon: '&#xe788;',
    roles: ['user', 'doctor', 'admin'],
    keepAlive: false
  },
  children: [
    {
      path: 'trend',
      name: 'RiskTrend',
      component: '/risk/trend',
      meta: {
        title: '风险趋势',
        icon: '&#xe7a3;',
        keepAlive: false,
        isHideTab: true,
        isHide: true
      }
    }
  ]
}
