declare namespace Http {
  /** 基础响应 */
  interface BaseResponse<T = unknown> {
    // 状态码
    code: number
    // 消息（兼容后端可能返回 msg 或 message）
    msg?: string
    message?: string
    // 数据
    data: T
  }
}
