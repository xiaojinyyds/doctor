<template>
  <ElDialog
    v-model="visible"
    title="历史评估对比分析"
    width="85vw"
    :close-on-click-modal="false"
    class="compare-dialog"
  >
    <div v-if="loading" class="loading-wrap">
      <ElSkeleton :rows="10" animated />
    </div>
    
    <div v-else-if="comparisonData" class="comparison-content">
      <!-- 对比概览 -->
      <ElCard class="overview-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a3;</i>
            <span>对比概览</span>
          </div>
        </template>
        
        <div class="overview-grid">
          <div class="time-info">
            <ElTag type="info" effect="dark" size="large">
              时间间隔：{{ comparisonData.time_diff_days }} 天
            </ElTag>
          </div>
          
          <div class="score-comparison">
            <div class="score-item">
              <div class="label">第一次评估</div>
              <div class="score">{{ (comparisonData.assessment_1.overall_risk.score * 100).toFixed(0) }}分</div>
              <div class="level" :style="{ color: getRiskColor(comparisonData.assessment_1.overall_risk.level) }">
                {{ comparisonData.assessment_1.overall_risk.level }}
              </div>
              <div class="date">{{ formatDate(comparisonData.assessment_1.created_at) }}</div>
            </div>
            
            <div class="arrow-container">
              <ElIcon :size="40" :color="getChangeColor(comparisonData.risk_score_change)">
                <component :is="getArrowIcon(comparisonData.risk_score_change)" />
              </ElIcon>
              <div class="change-text" :style="{ color: getChangeColor(comparisonData.risk_score_change) }">
                {{ comparisonData.risk_score_change > 0 ? '+' : '' }}{{ (comparisonData.risk_score_change * 100).toFixed(1) }}分
                ({{ comparisonData.risk_score_change_percentage > 0 ? '+' : '' }}{{ comparisonData.risk_score_change_percentage.toFixed(1) }}%)
              </div>
            </div>
            
            <div class="score-item">
              <div class="label">第二次评估</div>
              <div class="score">{{ (comparisonData.assessment_2.overall_risk.score * 100).toFixed(0) }}分</div>
              <div class="level" :style="{ color: getRiskColor(comparisonData.assessment_2.overall_risk.level) }">
                {{ comparisonData.assessment_2.overall_risk.level }}
              </div>
              <div class="date">{{ formatDate(comparisonData.assessment_2.created_at) }}</div>
            </div>
          </div>
          
          <div class="summary-box">
            <ElAlert
              :type="comparisonData.risk_score_change > 0 ? 'warning' : 'success'"
              :closable="false"
              show-icon
            >
              <template #title>
                <strong>{{ comparisonData.summary }}</strong>
              </template>
            </ElAlert>
          </div>
        </div>
      </ElCard>

      <!-- 分类风险对比 -->
      <ElCard class="category-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a5;</i>
            <span>各类肿瘤风险对比</span>
          </div>
        </template>
        
        <div class="table-wrapper">
          <ElTable :data="comparisonData.category_risks_comparison" stripe style="width: 100%; max-width: 1200px;">
            <ElTableColumn prop="category" label="肿瘤类型" width="180" fixed />
            <ElTableColumn label="第一次评估" align="center" width="240">
              <template #default="{ row }">
                <div class="score-cell">
                  <span>{{ (row.score_1 * 100).toFixed(0) }}分</span>
                  <ElTag :type="getScoreTagType(row.score_1 * 100)" size="small">
                    {{ getScoreLevel(row.score_1 * 100) }}
                  </ElTag>
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn label="第二次评估" align="center" width="240">
              <template #default="{ row }">
                <div class="score-cell">
                  <span>{{ (row.score_2 * 100).toFixed(0) }}分</span>
                  <ElTag :type="getScoreTagType(row.score_2 * 100)" size="small">
                    {{ getScoreLevel(row.score_2 * 100) }}
                  </ElTag>
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn label="变化" align="center" width="200">
              <template #default="{ row }">
                <div :style="{ color: getChangeColor(row.change) }">
                  <strong>{{ row.change > 0 ? '+' : '' }}{{ (row.change * 100).toFixed(1) }}分</strong>
                  <div style="font-size: 12px;">
                    ({{ row.change_percentage > 0 ? '+' : '' }}{{ row.change_percentage.toFixed(1) }}%)
                  </div>
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn label="趋势" align="center" width="120">
              <template #default="{ row }">
                <ElIcon :size="24" :color="getChangeColor(row.change)">
                  <component :is="getArrowIcon(row.change)" />
                </ElIcon>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </ElCard>

      <!-- 关键因素变化 -->
      <ElCard class="factors-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a3;</i>
            <span>关键风险因素变化</span>
          </div>
        </template>
        
        <div class="table-wrapper">
          <ElTable :data="comparisonData.key_factors_changes" stripe max-height="400" style="width: 100%; max-width: 1200px;">
            <ElTableColumn prop="factor" label="风险因素" width="220" fixed />
            <ElTableColumn label="第一次贡献度" align="center" width="200">
              <template #default="{ row }">
                {{ (row.contribution_1 * 100).toFixed(1) }}%
              </template>
            </ElTableColumn>
            <ElTableColumn label="第二次贡献度" align="center" width="200">
              <template #default="{ row }">
                {{ (row.contribution_2 * 100).toFixed(1) }}%
              </template>
            </ElTableColumn>
            <ElTableColumn label="变化" align="center" width="180">
              <template #default="{ row }">
                <span :style="{ color: getChangeColor(row.change) }">
                  {{ row.change > 0 ? '+' : '' }}{{ (row.change * 100).toFixed(1) }}%
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn label="状态" align="center" width="140">
              <template #default="{ row }">
                <ElTag
                  :type="row.status === 'improved' ? 'success' : row.status === 'worsened' ? 'danger' : 'info'"
                  size="small"
                >
                  {{ getStatusText(row.status) }}
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </ElCard>

      <!-- 改进建议 -->
      <ElCard class="suggestions-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe86e;</i>
            <span>改进建议</span>
          </div>
        </template>
        
        <div class="suggestions-list">
          <ElAlert
            v-for="(suggestion, index) in comparisonData.improvement_suggestions"
            :key="index"
            :type="index === 0 ? 'success' : 'info'"
            :closable="false"
            show-icon
          >
            <template #title>
              {{ suggestion }}
            </template>
          </ElAlert>
        </div>
      </ElCard>
    </div>
    
    <div v-else class="empty-state">
      <ElEmpty description="暂无对比数据" />
    </div>
    
    <template #footer>
      <ElButton type="primary" @click="close">关闭</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'
import request from '@/utils/http'

const props = defineProps<{
  modelValue: boolean
  id1: string | null
  id2: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()

const visible = ref(false)
const loading = ref(false)
const comparisonData = ref<any>(null)

watch(
  () => props.modelValue,
  async (v) => {
    visible.value = v
    if (v && props.id1 && props.id2) {
      await loadComparison()
    }
  },
  { immediate: true }
)

watch(visible, (v) => emit('update:modelValue', v))

/**
 * 加载对比数据
 */
async function loadComparison() {
  if (!props.id1 || !props.id2) {
    ElMessage.error('请选择两条评估记录')
    return
  }
  
  loading.value = true
  comparisonData.value = null
  
  try {
    const res: any = await request.get({
      url: '/api/v1/assessment/compare',
      params: {
        id1: props.id1,
        id2: props.id2
      }
    })
    
    comparisonData.value = res.data || res
    console.log('对比数据:', comparisonData.value)
  } catch (error) {
    console.error('加载对比数据失败:', error)
    ElMessage.error('加载对比数据失败')
  } finally {
    loading.value = false
  }
}

function close() {
  visible.value = false
}

// 辅助函数
function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function getRiskColor(level: string): string {
  const colorMap: Record<string, string> = {
    '低风险': '#52c41a',
    '中风险': '#faad14',
    '高风险': '#fa8c16',
    '极高风险': '#f5222d'
  }
  return colorMap[level] || '#999'
}

function getChangeColor(change: number): string {
  if (change > 0) return '#f5222d' // 上升-红色
  if (change < 0) return '#52c41a' // 下降-绿色
  return '#999' // 不变-灰色
}

function getArrowIcon(change: number) {
  if (change > 0.01) return ArrowUp
  if (change < -0.01) return ArrowDown
  return Minus
}

function getScoreLevel(score: number): string {
  if (score < 40) return '低风险'
  if (score < 60) return '中风险'
  if (score < 80) return '高风险'
  return '极高风险'
}

function getScoreTagType(score: number): 'success' | 'warning' | 'danger' | 'info' {
  if (score < 40) return 'success'
  if (score < 60) return 'warning'
  if (score < 80) return 'warning'
  return 'danger'
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'improved': '改善',
    'worsened': '恶化',
    'stable': '稳定'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.compare-dialog :deep(.el-dialog__body) {
  padding: 15px;
  max-height: 75vh;
  overflow-y: auto;
}

.loading-wrap {
  padding: 20px;
}

.comparison-content {
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    
    .iconfont-sys {
      font-size: 18px;
      color: var(--el-color-primary);
    }
  }
}

/* 概览卡片 */
.overview-card {
  margin-bottom: 20px;
  
  .overview-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
    
    .time-info {
      text-align: center;
    }
    
    .score-comparison {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      gap: 30px;
      align-items: center;
      
      .score-item {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        border-radius: 8px;
        
        .label {
          font-size: 14px;
          color: #606266;
          margin-bottom: 10px;
        }
        
        .score {
          font-size: 42px;
          font-weight: bold;
          color: var(--el-color-primary);
          margin: 10px 0;
        }
        
        .level {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
        }
        
        .date {
          font-size: 12px;
          color: #909399;
        }
      }
      
      .arrow-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        
        .change-text {
          font-size: 16px;
          font-weight: bold;
          white-space: nowrap;
        }
      }
    }
    
    .summary-box {
      margin-top: 10px;
    }
  }
}

/* 分类风险卡片 */
.category-card {
  margin-bottom: 20px;
  
  .table-wrapper {
    display: flex;
    justify-content: center;
  }
  
  .score-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
}

/* 关键因素卡片 */
.factors-card {
  margin-bottom: 20px;
  
  .table-wrapper {
    display: flex;
    justify-content: center;
  }
}

/* 改进建议卡片 */
.suggestions-card {
  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}

.empty-state {
  padding: 40px;
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .overview-grid {
    .score-comparison {
      grid-template-columns: 1fr !important;
      gap: 20px !important;
      
      .arrow-container {
        transform: rotate(90deg);
      }
    }
  }
}
</style>

