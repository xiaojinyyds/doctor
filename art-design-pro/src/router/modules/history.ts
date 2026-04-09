import { AppRouteRecord } from '@/types/router'

/**
 * 历史记录路由
 * 所有用户都可访问
 */
export const historyRoutes: AppRouteRecord = {
  path: '/history',
  name: 'History',
  component: '/index/index',
  meta: {
    title: '筛查历史',
    icon: '&#xe7b5;', // 历史图标
    roles: ['user', 'doctor', 'admin'],
    keepAlive: true
  },
  children: [
    {
      path: 'list',
      name: 'HistoryList',
      component: '/history/index',
      meta: {
        title: '历史记录',
        keepAlive: true
      }
    },
    {
      path: 'compare',
      name: 'HistoryCompare',
      component: '/history/compare',
      meta: {
        title: '对比分析',
        keepAlive: false,
        isHide: true
      }
    }
  ]
}

