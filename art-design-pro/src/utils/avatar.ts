/**
 * 头像工具函数
 * 根据用户角色返回对应的默认头像
 */

/**
 * 获取用户头像URL
 * 优先使用用户自定义头像，如果没有则根据角色返回默认头像
 * 
 * @param userInfo 用户信息
 * @returns 头像URL
 */
export function getUserAvatar(userInfo: Partial<Api.Auth.UserInfo>): string {
  // 如果用户有自定义头像，优先使用
  if (userInfo.avatar) {
    return userInfo.avatar
  }

  // 根据角色返回默认头像
  const role = userInfo.roles?.[0] || 'user'
  
  return getRoleAvatar(role)
}

/**
 * 根据角色获取默认头像
 * 
 * @param role 用户角色
 * @returns 头像路径
 */
export function getRoleAvatar(role: string): string {
  const avatarMap: Record<string, string> = {
    'admin': '/admin.png',
    'doctor': '/doctor.png',
    'user': '/user.png'
  }

  return avatarMap[role] || avatarMap['user']
}

/**
 * 获取角色显示名称
 * 
 * @param role 用户角色
 * @returns 角色中文名称
 */
export function getRoleName(role: string): string {
  const roleNameMap: Record<string, string> = {
    'admin': '管理员',
    'doctor': '医生',
    'user': '普通用户'
  }

  return roleNameMap[role] || '用户'
}

