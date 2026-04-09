import { AppRouteRecord } from '@/types/router'

export const systemRoutes: AppRouteRecord = {
  path: '/system',
  name: 'System',
  component: '/index/index',
  meta: {
    title: 'menus.system.title',
    icon: '&#xe7b9;',
    roles: ['R_SUPER', 'admin']
  },
  children: [
    {
      path: 'user',
      name: 'User',
      component: '/system/user',
      meta: {
        title: 'menus.system.user',
        keepAlive: true,
        roles: ['admin']
      }
    },
    {
      path: 'role',
      name: 'Role',
      component: '/system/role',
      meta: {
        title: 'menus.system.role',
        keepAlive: true,
        roles: ['R_SUPER']
      }
    },
    {
      path: 'screening-records',
      name: 'ScreeningRecords',
      component: '/system/screening-records',
      meta: {
        title: 'menus.system.screeningRecords',
        keepAlive: true,
        roles: ['R_SUPER', 'admin']
      }
    },
    {
      path: 'screening-records/detail/:id',
      name: 'ScreeningRecordDetail',
      component: '/system/screening-records/detail',
      meta: {
        title: '筛查记录详情',
        isHide: true,
        keepAlive: false,
        isHideTab: true,
        roles: ['R_SUPER', 'admin']
      }
    },
    {
      path: 'statistics',
      name: 'Statistics',
      component: '/system/statistics',
      meta: {
        title: 'menus.system.statistics',
        keepAlive: true,
        roles: ['R_SUPER', 'admin']
      }
    },
    {
      path: 'user-center',
      name: 'UserCenter',
      component: '/system/user-center',
      meta: {
        title: 'menus.system.userCenter',
        isHide: true,
        keepAlive: true,
        isHideTab: true
      }
    },
    {
      path: 'user-docs',
      name: 'UserDocs',
      component: '/system/user-docs',
      meta: {
        title: '使用文档',
        isHide: true,
        keepAlive: true,
        isHideTab: true
      }
    },
    {
      path: 'menu',
      name: 'Menus',
      component: '/system/menu',
      meta: {
        title: 'menus.system.menu',
        keepAlive: true,
        roles: ['R_SUPER'],
        authList: [
          { title: '新增', authMark: 'add' },
          { title: '编辑', authMark: 'edit' },
          { title: '删除', authMark: 'delete' }
        ]
      }
    }
  ]
}
