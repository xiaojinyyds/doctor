import { AppRouteRecord } from '@/types/router'

/**
 * 医学影像分析路由
 * user, doctor, admin 都可访问
 */
export const medicalImageRoutes: AppRouteRecord = {
  path: '/medical-image',
  name: 'MedicalImage',
  component: '/index/index',
  redirect: '/medical-image/upload',
  meta: {
    title: '影像识别',
    icon: '&#xe667;', // 图像图标
    roles: ['user', 'doctor', 'admin'],
    keepAlive: true
  },
  children: [
    {
      path: '/medical-image/upload',
      name: 'MedicalImageUpload',
      component: '/medical-image/upload',
      meta: {
        title: '影像上传',
        icon: '&#xe621;',
        roles: ['user', 'doctor', 'admin'],
        keepAlive: false
      }
    },
    {
      path: '/medical-image/history',
      name: 'MedicalImageHistory',
      component: '/medical-image/history',
      meta: {
        title: '历史记录',
        icon: '&#xe63c;',
        roles: ['user', 'doctor', 'admin'],
        keepAlive: true
      }
    },
    {
      path: '/medical-image/statistics',
      name: 'MedicalImageStatistics',
      component: '/medical-image/statistics',
      meta: {
        title: '数据统计',
        icon: '&#xe61b;',
        roles: ['user', 'doctor', 'admin'],
        keepAlive: true
      }
    }
  ]
}

