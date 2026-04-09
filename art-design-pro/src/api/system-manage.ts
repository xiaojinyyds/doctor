import request from '@/utils/http'
import { AppRouteRecord } from '@/types/router'

// 获取用户列表
export function fetchGetUserList(params: Api.SystemManage.UserSearchParams) {
  return request.get({
    url: '/api/v1/admin/users',
    params
  })
}

// 删除用户
export function fetchDeleteUser(userId: string) {
  return request.del({
    url: `/api/v1/admin/users/${userId}`
  })
}

// 更新用户状态
export function fetchUpdateUserStatus(userId: string, status: 'active' | 'disabled') {
  return request.put({
    url: `/api/v1/admin/users/${userId}/status`,
    data: {
      status
    }
  })
}

// 新增用户（管理员）
export function fetchCreateUser(data: { 
  email: string; 
  nickname: string; 
  role: 'user' | 'doctor' | 'admin';
  phone?: string 
}) {
  return request.post({
    url: '/api/v1/admin/users',
    data
  })
}

// 更新用户角色
export function fetchUpdateUserRole(userId: string, role: 'user' | 'doctor' | 'admin') {
  return request.put({
    url: `/api/v1/admin/users/${userId}/role`,
    data: {
      role
    }
  })
}

// 重置用户密码
export function fetchResetUserPassword(userId: string, newPassword: string) {
  return request.post({
    url: `/api/v1/admin/users/${userId}/reset-password`,
    data: {
      new_password: newPassword
    }
  })
}

// 获取角色列表
export function fetchGetRoleList(params: Api.SystemManage.RoleSearchParams) {
  return request.get<Api.SystemManage.RoleList>({
    url: '/api/role/list',
    params
  })
}

// 获取菜单列表
export function fetchGetMenuList() {
  return request.get<AppRouteRecord[]>({
    url: '/api/system/menus'
  })
}
