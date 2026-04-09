import request from '@/utils/http'

/**
 * 登录
 * @param params 登录参数
 * @returns 登录响应
 */
export function fetchLogin(params: Api.Auth.LoginParams) {
  return request
    .post<any>({
      url: '/api/v1/auth/login',
      data: params,
      headers: { 'Content-Type': 'application/json' },
      showErrorMessage: true
    })
    .then((res: any) => {
      // 适配后端返回的数据格式
      return {
        token: res.access_token || res.token,
        refreshToken: res.refresh_token || ''
      } as Api.Auth.LoginResponse
    })
}

/**
 * 获取用户信息
 * @returns 用户信息
 */
export function fetchGetUserInfo() {
  return request
    .get<any>({
      url: '/api/v1/auth/me'
    })
    .then((res: any) => {
      // 后端返回格式: { code: 200, message: "...", data: {...} }
      const userData = res.data || res
      
      // 适配后端返回的用户信息格式
      return {
        userId: userData.id || 0,
        userName: userData.nickname || userData.email || '',
        email: userData.email || '',
        avatar: userData.avatar_url || '',
        roles: [userData.role || 'user'],
        buttons: []
      } as Api.Auth.UserInfo
    })
}

/**
 * 获取个人中心详细信息
 * @returns 包含用户信息、统计数据、最新活动等
 */
export function fetchUserProfile() {
  return request.get<any>({
    url: '/api/v1/auth/profile'
  })
}

/**
 * 注册
 * @param params 注册参数
 */
export function fetchRegister(params: Api.Auth.RegisterParams) {
  console.log(JSON.stringify(params))
  return request.post<any>({
    url: '/api/v1/auth/register',
    data: JSON.stringify(params),
    headers: { 'Content-Type': 'application/json' },
    showSuccessMessage: false
  })
}

/**
 * 发送邮箱验证码
 * @param params { email }
 */
export function fetchSendCode(params: Api.Auth.SendCodeParams) {
  return request.post<any>({
    url: '/api/v1/auth/send-code',
    data: params,
    showSuccessMessage: false
  })
}

/**
 * 更新用户信息
 * @param data 用户信息
 */
export function updateUserProfile(data: { nickname?: string; phone?: string; avatar_url?: string }) {
  return request.put<any>({
    url: '/api/v1/auth/update-profile',
    data,
    showSuccessMessage: true
  })
}

/**
 * 修改密码
 * @param data 密码信息
 */
export function changePassword(data: { old_password: string; new_password: string }) {
  return request.post<any>({
    url: '/api/v1/auth/change-password',
    data,
    showSuccessMessage: true
  })
}
