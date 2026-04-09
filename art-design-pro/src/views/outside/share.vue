<template>
  <div class="share-page">
    <div class="share-container">
      <!-- 头部 -->
      <div class="share-header">
        <h1>肿瘤风险评估报告</h1>
        <p>此报告由「肿瘤数智化筛查系统」生成</p>
      </div>

      <!-- 需要密码 -->
      <div v-if="needPassword && !isUnlocked" class="password-box">
        <ElCard shadow="hover">
          <div class="password-content">
            <ElIcon :size="60" color="#faad14"><Lock /></ElIcon>
            <h3>此报告需要访问密码</h3>
            <ElForm style="width: 300px; margin-top: 20px;">
              <ElFormItem>
                <ElInput
                  v-model="password"
                  type="password"
                  placeholder="请输入访问密码"
                  show-password
                  @keyup.enter="unlockReport"
                />
              </ElFormItem>
              <ElFormItem>
                <ElButton
                  type="primary"
                  style="width: 100%"
                  :loading="loading"
                  @click="unlockReport"
                >
                  解锁查看
                </ElButton>
              </ElFormItem>
            </ElForm>
          </div>
        </ElCard>
      </div>

      <!-- 报告内容 -->
      <div v-else-if="reportData" v-loading="loading" class="report-content">
        <!-- 风险总览 -->
        <ElCard class="report-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>综合风险评估</span>
            </div>
          </template>
          <div class="risk-overview">
            <div class="risk-score">
              <div class="score-value" :style="{ color: getRiskColor(reportData.overall_risk.level) }">
                {{ (reportData.overall_risk.score * 100).toFixed(0) }}
              </div>
              <div class="score-label">风险分数</div>
            </div>
            <div class="risk-detail">
              <h2 :style="{ color: getRiskColor(reportData.overall_risk.level) }">
                {{ reportData.overall_risk.level }}
              </h2>
              <p>
                风险评分为 <strong>{{ (reportData.overall_risk.score * 100).toFixed(0) }}</strong> 分，
                比 <strong>{{ reportData.overall_risk.percentile }}%</strong> 的同龄人风险更高。
              </p>
              <div class="user-info">
                <span>年龄：{{ reportData.user_info.age }}岁</span>
                <span>性别：{{ reportData.user_info.gender }}</span>
                <span>BMI：{{ reportData.user_info.bmi?.toFixed(1) || '-' }}</span>
              </div>
            </div>
          </div>
        </ElCard>

        <!-- 分类风险 -->
        <ElCard class="report-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>各类肿瘤风险细分</span>
            </div>
          </template>
          <div class="category-list">
            <div
              v-for="([name, data], index) in Object.entries(reportData.category_risks)"
              :key="index"
              class="category-item"
            >
              <span class="category-name">{{ name }}</span>
              <ElProgress
                :percentage="data.score * 100"
                :color="getProgressColor(data.score * 100)"
                :stroke-width="16"
              />
              <ElTag :type="getRiskTagType(data.level)" size="small">
                {{ data.level }}
              </ElTag>
            </div>
          </div>
        </ElCard>

        <!-- 关键因素 -->
        <ElCard class="report-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>关键风险因素</span>
            </div>
          </template>
          <div class="factors-list">
            <div
              v-for="(factor, index) in reportData.key_factors"
              :key="index"
              class="factor-item"
            >
              <div class="factor-header">
                <span class="factor-name">{{ factor.factor }}</span>
                <ElTag
                  :type="factor.direction === 'increase' ? 'danger' : 'success'"
                  size="small"
                >
                  {{ factor.direction === 'increase' ? '增加风险' : '降低风险' }}
                </ElTag>
              </div>
              <p class="factor-desc">{{ factor.description }}</p>
            </div>
          </div>
        </ElCard>

        <!-- 健康建议 -->
        <ElCard class="report-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>健康建议</span>
            </div>
          </template>
          <div class="recommendations-list">
            <div
              v-for="(rec, index) in reportData.recommendations"
              :key="index"
              class="rec-item"
            >
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.content }}</p>
            </div>
          </div>
        </ElCard>

        <!-- 免责声明 -->
        <ElCard class="disclaimer-card" shadow="never">
          <ElAlert type="warning" :closable="false" show-icon>
            <template #title>
              <strong>免责声明</strong>
            </template>
            本系统提供的风险评估结果仅供参考，不构成医疗诊断。如有健康问题，请及时就医并咨询专业医生。
          </ElAlert>
        </ElCard>

        <!-- 访问统计 -->
        <div class="view-count">
          <ElIcon><View /></ElIcon>
          <span>此报告已被查看 {{ reportData.view_count }} 次</span>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <ElResult icon="error" :title="errorMessage">
          <template #extra>
            <ElButton type="primary" @click="goHome">返回首页</ElButton>
          </template>
        </ElResult>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ElMessage, 
  ElCard, 
  ElIcon, 
  ElForm, 
  ElFormItem, 
  ElInput, 
  ElButton,
  ElProgress,
  ElTag,
  ElAlert,
  ElResult
} from 'element-plus'
import { Lock, View } from '@element-plus/icons-vue'
import request from '@/utils/http'

// 定义报告数据类型
interface RiskData {
  score: number
  level: string
}

interface KeyFactor {
  factor: string
  direction: 'increase' | 'decrease'
  description: string
}

interface Recommendation {
  title: string
  content: string
}

interface UserInfo {
  age: number
  gender: string
  bmi?: number
}

interface ReportData {
  overall_risk: RiskData & { percentile: number }
  user_info: UserInfo
  category_risks: Record<string, RiskData>
  key_factors: KeyFactor[]
  recommendations: Recommendation[]
  view_count: number
}

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const reportData = ref<ReportData | null>(null)
const needPassword = ref(false)
const isUnlocked = ref(false)
const password = ref('')
const error = ref(false)
const errorMessage = ref('')

onMounted(() => {
  loadSharedReport()
})

/**
 * 加载分享的报告
 */
async function loadSharedReport(pwd?: string) {
  const token = route.params.token as string
  
  if (!token) {
    error.value = true
    errorMessage.value = '分享链接无效'
    loading.value = false
    return
  }
  
  loading.value = true
  
  try {
    const res: any = await request.get({
      url: `/api/v1/share/${token}`,
      params: pwd ? { password: pwd } : {}
    })
    
    reportData.value = res.data || res
    isUnlocked.value = true
    loading.value = false
    
  } catch (err: any) {
    loading.value = false
    
    const status = err?.response?.status
    const detail = err?.response?.data?.detail || err?.message
    
    if (status === 401 && detail?.includes('密码')) {
      // 需要密码
      needPassword.value = true
      if (pwd) {
        ElMessage.error('密码错误')
      }
    } else if (status === 410) {
      // 链接过期
      error.value = true
      errorMessage.value = '分享链接已过期'
    } else if (status === 404) {
      // 链接不存在
      error.value = true
      errorMessage.value = '分享链接不存在或已失效'
    } else {
      error.value = true
      errorMessage.value = detail || '加载失败'
    }
  }
}

/**
 * 解锁报告
 */
function unlockReport() {
  if (!password.value) {
    ElMessage.warning('请输入密码')
    return
  }
  
  loadSharedReport(password.value)
}

/**
 * 返回首页
 */
function goHome() {
  router.push('/')
}

// 辅助函数
function getRiskColor(level: string): string {
  const colorMap: Record<string, string> = {
    '低风险': '#52c41a',
    '中风险': '#faad14',
    '高风险': '#fa8c16',
    '极高风险': '#f5222d'
  }
  return colorMap[level] || '#999'
}

function getProgressColor(value: number): string {
  if (value < 40) return '#52c41a'
  if (value < 60) return '#faad14'
  if (value < 80) return '#fa8c16'
  return '#f5222d'
}

function getRiskTagType(level: string): 'success' | 'warning' | 'danger' | 'info' {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    '低风险': 'success',
    '中风险': 'warning',
    '高风险': 'danger',
    '极高风险': 'danger'
  }
  return typeMap[level] || 'info'
}
</script>

<style scoped lang="scss">
.share-page {
  min-height: 100vh;
  background: var(--art-main-bg-color);
  padding: 20px;
  
  .share-container {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .share-header {
    text-align: center;
    background: var(--art-main-bg-color);
    padding: 30px 20px;
    margin-bottom: 30px;
    border-radius: 8px;
    border-bottom: 3px solid var(--el-color-primary);
    
    h1 {
      font-size: 28px;
      margin: 0 0 10px 0;
      color: var(--art-text-gray-800);
    }
    
    p {
      font-size: 14px;
      color: var(--art-text-gray-500);
      margin: 0;
    }
  }
  
  .password-box {
    display: flex;
    justify-content: center;
    
    .password-content {
      text-align: center;
      padding: 40px;
      
      h3 {
        margin: 20px 0;
        color: #606266;
      }
    }
  }
  
  .report-content {
    .report-card {
      margin-bottom: 20px;
      
      .card-header {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .risk-overview {
      display: flex;
      gap: 40px;
      align-items: center;
      
      .risk-score {
        flex: 1;
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        
        .score-value {
          font-size: 72px;
          font-weight: bold;
          line-height: 1;
        }
        
        .score-label {
          font-size: 16px;
          color: #909399;
          margin-top: 10px;
        }
      }
      
      .risk-detail {
        flex: 1;
        
        h2 {
          font-size: 32px;
          margin: 0 0 15px 0;
        }
        
        p {
          font-size: 16px;
          line-height: 1.8;
          color: #606266;
          
          strong {
            color: var(--el-color-primary);
          }
        }
        
        .user-info {
          display: flex;
          gap: 20px;
          margin-top: 15px;
          font-size: 14px;
          color: #909399;
        }
      }
    }
    
    .category-list {
      .category-item {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
        
        .category-name {
          width: 100px;
          font-size: 14px;
        }
        
        .el-progress {
          flex: 1;
        }
        
        .el-tag {
          min-width: 70px;
          text-align: center;
        }
      }
    }
    
    .factors-list {
      .factor-item {
        padding: 15px;
        margin-bottom: 12px;
        background: #f5f7fa;
        border-radius: 8px;
        border-left: 4px solid var(--el-color-primary);
        
        .factor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          .factor-name {
            font-size: 15px;
            font-weight: 600;
          }
        }
        
        .factor-desc {
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
          margin: 0;
        }
      }
    }
    
    .recommendations-list {
      .rec-item {
        padding: 15px;
        margin-bottom: 12px;
        background: #f0f9ff;
        border-radius: 8px;
        
        h4 {
          margin: 0 0 10px 0;
          color: #303133;
          font-size: 16px;
        }
        
        p {
          margin: 0;
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
    
    .disclaimer-card {
      margin-top: 30px;
      background: #fffbe6;
      border: 1px solid #ffe58f;
    }
    
    .view-count {
      text-align: center;
      margin-top: 20px;
      padding: 15px;
      font-size: 14px;
      color: var(--art-text-gray-500);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--art-main-bg-color);
      border-radius: 8px;
    }
  }
  
  .error-state {
    background: var(--art-main-bg-color);
    border-radius: 12px;
    padding: 40px;
  }
}

@media (max-width: 768px) {
  .share-page {
    padding: 20px 10px;
    
    .risk-overview {
      flex-direction: column !important;
    }
  }
}
</style>

