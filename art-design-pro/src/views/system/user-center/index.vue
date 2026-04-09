<template>
  <div class="user-center-container" v-loading="loading">
    <!-- 用户信息卡片 -->
    <el-card class="profile-card" shadow="hover">
      <div class="profile-header">
        <div class="avatar-section">
          <img class="user-avatar" :src="userAvatar" alt="用户头像" />
          <div class="user-basic">
            <h2 class="user-name">{{ userInfo.userName }}</h2>
            <div class="user-meta">
              <el-tag type="primary" size="small">{{ userRoleName }}</el-tag>
              <span class="user-email">
                <i class="el-icon-message"></i>
                {{ profileData?.user.email }}
              </span>
            </div>
          </div>
        </div>
        <div class="profile-stats">
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(64, 158, 255, 0.1)">
              <i class="el-icon-document" style="color: #409eff"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ profileData?.statistics.total.questionnaire_count || 0 }}</div>
              <div class="stat-label">问卷记录</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(103, 194, 58, 0.1)">
              <i class="el-icon-data-analysis" style="color: #67c23a"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ profileData?.statistics.total.assessment_count || 0 }}</div>
              <div class="stat-label">风险评估</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: rgba(230, 162, 60, 0.1)">
              <i class="el-icon-picture" style="color: #e6a23c"></i>
              </div>
            <div class="stat-info">
              <div class="stat-value">{{ profileData?.statistics.total.image_count || 0 }}</div>
              <div class="stat-label">影像上传</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 详细信息和设置 -->
    <el-row :gutter="20">
      <!-- 基本信息 -->
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>
                <i class="el-icon-user"></i>
                基本信息
              </span>
              <el-button type="primary" text @click="toggleEdit">
                <i :class="isEdit ? 'el-icon-check' : 'el-icon-edit'"></i>
                {{ isEdit ? '保存' : '编辑' }}
              </el-button>
            </div>
          </template>

          <el-form :model="form" ref="formRef" :rules="rules" label-width="80px">
            <el-form-item label="昵称" prop="nikeName">
              <el-input v-model="form.nikeName" :disabled="!isEdit" placeholder="请输入昵称" />
            </el-form-item>

            <el-form-item label="手机号" prop="mobile">
              <el-input v-model="form.mobile" :disabled="!isEdit" placeholder="请输入手机号" />
            </el-form-item>

            <el-form-item label="邮箱">
              <el-input v-model="form.email" disabled />
            </el-form-item>

            <el-form-item label="注册时间">
              <el-input :value="formatDate(profileData?.user.created_at)" disabled />
            </el-form-item>

            <el-form-item label="最后登录">
              <el-input :value="formatDateTime(profileData?.user.last_login_at)" disabled />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 修改密码 -->
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>
                <i class="el-icon-lock"></i>
                修改密码
              </span>
        </div>
          </template>

          <el-form :model="pwdForm" ref="pwdFormRef" :rules="pwdRules" label-width="100px">
            <el-form-item label="当前密码" prop="password">
              <el-input
                v-model="pwdForm.password"
                type="password"
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="pwdForm.newPassword"
                type="password"
                placeholder="请输入新密码（至少6位）"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                v-model="pwdForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
                <i class="el-icon-check"></i>
                修改密码
              </el-button>
              <el-button @click="resetPwdForm">
                <i class="el-icon-refresh-left"></i>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card class="activity-card" shadow="hover" v-if="profileData?.latest_activity">
      <template #header>
        <div class="card-header">
          <span>
            <i class="el-icon-time"></i>
            最近活动
          </span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :md="12" v-if="profileData.latest_activity.latest_assessment">
          <div class="activity-item">
            <div class="activity-icon assessment">
              <i class="el-icon-data-line"></i>
            </div>
            <div class="activity-content">
              <h4>最新风险评估</h4>
              <p class="activity-desc">
                风险等级: 
                <el-tag :type="getRiskType(profileData.latest_activity.latest_assessment.overall_risk_level)" size="small">
                  {{ profileData.latest_activity.latest_assessment.overall_risk_level }}
                </el-tag>
              </p>
              <p class="activity-time">
                {{ formatDateTime(profileData.latest_activity.latest_assessment.created_at) }}
              </p>
        </div>
          </div>
        </el-col>

        <el-col :xs="24" :md="12" v-if="profileData.latest_activity.latest_image_analysis">
          <div class="activity-item">
            <div class="activity-icon image">
              <i class="el-icon-picture"></i>
            </div>
            <div class="activity-content">
              <h4>最新影像分析</h4>
              <p class="activity-desc">
                预测结果: 
                <el-tag :type="getRiskType(profileData.latest_activity.latest_image_analysis.risk_level)" size="small">
                  {{ profileData.latest_activity.latest_image_analysis.predicted_class }}
                </el-tag>
              </p>
              <p class="activity-time">
                {{ formatDateTime(profileData.latest_activity.latest_image_analysis.created_at) }}
              </p>
      </div>
    </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
  import { useUserStore } from '@/store/modules/user'
  import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserAvatar, getRoleName } from '@/utils/avatar'
import { fetchUserProfile, updateUserProfile, changePassword } from '@/api/auth'

  defineOptions({ name: 'UserCenter' })

  const userStore = useUserStore()
  const userInfo = computed(() => userStore.getUserInfo)

// 根据角色获取头像和角色名
const userAvatar = computed(() => getUserAvatar(userInfo.value))
const userRoleName = computed(() => getRoleName(userInfo.value.roles?.[0] || 'user'))

// 个人资料详细数据
const profileData = ref<any>(null)
const loading = ref(false)

// 表单状态
  const isEdit = ref(false)
const changingPassword = ref(false)
const formRef = ref<FormInstance>()
const pwdFormRef = ref<FormInstance>()

// 用户信息表单
  const form = reactive({
  nikeName: '',
  email: '',
  mobile: ''
  })

// 密码修改表单
  const pwdForm = reactive({
  password: '',
  newPassword: '',
  confirmPassword: ''
  })

// 表单验证规则
  const rules = reactive<FormRules>({
    nikeName: [
      { required: true, message: '请输入昵称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
})

// 密码验证规则
const pwdRules = reactive<FormRules>({
  password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

// 加载个人资料
const loadProfile = async () => {
  loading.value = true
  try {
    const response: any = await fetchUserProfile()
    profileData.value = response

    // 填充表单数据
    if (response.user) {
      form.nikeName = response.user.nickname || ''
      form.email = response.user.email || ''
      form.mobile = response.user.phone || ''
    }
  } catch (error) {
    ElMessage.error('加载个人资料失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 切换编辑状态
const toggleEdit = async () => {
  if (isEdit.value) {
    // 保存
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
      if (valid) {
        try {
          await updateUserProfile({
            nickname: form.nikeName,
            phone: form.mobile || undefined
          })
          isEdit.value = false
          await loadProfile() // 重新加载数据
        } catch (error: any) {
          ElMessage.error(error.message || '更新失败')
        }
      }
    })
  } else {
    isEdit.value = true
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!pwdFormRef.value) return

  await pwdFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        changingPassword.value = true
        await changePassword({
          old_password: pwdForm.password,
          new_password: pwdForm.newPassword
        })
        resetPwdForm()
        ElMessage.success('密码修改成功，请重新登录')
        
        // 2秒后退出登录
        setTimeout(() => {
          userStore.logOut()
        }, 2000)
      } catch (error: any) {
        ElMessage.error(error.message || '密码修改失败')
      } finally {
        changingPassword.value = false
      }
    }
  })
}

// 重置密码表单
const resetPwdForm = () => {
  pwdForm.password = ''
  pwdForm.newPassword = ''
  pwdForm.confirmPassword = ''
  pwdFormRef.value?.clearValidate()
  }

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '未设置'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取风险标签类型
const getRiskType = (riskLevel: string) => {
  if (riskLevel?.includes('低')) return 'success'
  if (riskLevel?.includes('中')) return 'warning'
  return 'danger'
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped lang="scss">
.user-center-container {
  padding: 20px;
}

.profile-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 0;
  }

  .profile-header {
    padding: 32px;
    background: linear-gradient(to right, #f5f7fa 0%, #e8f4f8 100%);

    .avatar-section {
      display: flex;
      align-items: center;
      gap: 24px;
      margin-bottom: 32px;

      .user-avatar {
        width: 100px;
        height: 100px;
            border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          }

      .user-basic {
        flex: 1;

        .user-name {
          font-size: 28px;
          font-weight: 600;
          margin: 0 0 12px 0;
          color: #303133;
          }

        .user-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          flex-wrap: wrap;

          .user-email {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #606266;
            font-size: 14px;
          }
        }
      }
    }

    .profile-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;

      .stat-card {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;
        background: white;
        border-radius: 12px;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        }

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
              display: flex;
          align-items: center;
              justify-content: center;
          font-size: 28px;
          flex-shrink: 0;
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 32px;
            font-weight: 600;
            color: #303133;
            line-height: 1;
            margin-bottom: 8px;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
              }
            }
          }
        }

.info-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    font-weight: 600;

    span {
      display: flex;
      align-items: center;
      gap: 8px;
          }
        }
      }

.activity-card {
  .activity-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      background: var(--el-fill-color-light);
              }

    .activity-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
              display: flex;
              align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;

      &.assessment {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
              }

      &.image {
        background: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }
    }

    .activity-content {
      flex: 1;

      h4 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
        }

      .activity-desc {
        margin: 0 0 6px 0;
        color: #606266;
        font-size: 14px;
      }

      .activity-time {
        margin: 0;
        color: #909399;
        font-size: 13px;
        }
      }
    }
  }
</style>
