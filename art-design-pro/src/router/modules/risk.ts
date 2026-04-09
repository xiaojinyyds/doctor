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
  }
}
