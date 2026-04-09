<template>
  <div class="screening-detail-container">
    <!-- 顶部操作栏 -->
    <div class="detail-header">
      <div class="header-left">
        <i class="iconfont-sys">&#xe7b9;</i>
        <div class="header-text">
          <h1>筛查记录详情</h1>
          <p>记录ID: {{ recordId }}</p>
        </div>
      </div>
      <div class="header-actions">
        <ElButton @click="goBack">
          <i class="iconfont-sys">&#xe625;</i>
          返回列表
        </ElButton>
        <!-- <ElButton type="primary" @click="exportRecord" :loading="exportLoading">
          <i class="iconfont-sys">&#xe7a8;</i>
          导出报告
        </ElButton>
        <ElButton type="danger" @click="deleteRecord">
          <i class="iconfont-sys">&#xe7a9;</i>
          删除记录
        </ElButton> -->
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" element-loading-text="正在加载记录详情..." class="detail-content">
      <!-- 用户基本信息 -->
      <ElCard class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7b0;</i>
            <span>用户信息</span>
          </div>
        </template>
        <div class="user-info-grid">
          <div class="info-item">
            <label>用户ID</label>
            <span>{{ detailData.user.id || '-' }}</span>
          </div>
          <div class="info-item">
            <label>用户昵称</label>
            <span>{{ detailData.user.nickname || '-' }}</span>
          </div>
          <div class="info-item">
            <label>用户邮箱</label>
            <span>{{ detailData.user.email || '-' }}</span>
          </div>
          <div class="info-item">
            <label>电话</label>
            <span>{{ detailData.user.phone || '-' }}</span>
          </div>
          <div class="info-item">
            <label>用户状态</label>
            <ElTag :type="detailData.user.status === 'active' ? 'success' : 'info'" size="small">
              {{ detailData.user.status === 'active' ? '活跃' : detailData.user.status || '-' }}
            </ElTag>
          </div>
          <div class="info-item">
            <label>评估时间</label>
            <span>{{ detailData.user.created_at || '-' }}</span>
          </div>
        </div>
      </ElCard>

      <!-- 评估信息 -->
      <ElCard v-if="assessmentInfo" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a2;</i>
            <span>评估信息</span>
          </div>
        </template>
        <div class="assessment-info-grid">
          <div class="info-item">
            <label>评估ID</label>
            <span>{{ assessmentInfo.id || '-' }}</span>
          </div>
          <div class="info-item">
            <label>评估时间</label>
            <span>{{ assessmentInfo.created_at || '-' }}</span>
          </div>
          <div class="info-item">
            <label>模型版本</label>
            <ElTag type="primary" size="small">{{ assessmentInfo.model_version || '-' }}</ElTag>
          </div>
          <div class="info-item">
            <label>推理耗时</label>
            <span>{{ assessmentInfo.inference_time_ms || 0 }}ms</span>
          </div>
          <div class="info-item">
            <label>风险等级</label>
            <span
              class="risk-level-text"
              :style="{ color: getRiskColor(assessmentInfo.overall_risk?.level || '') }"
            >
              {{ assessmentInfo.overall_risk?.level || '-' }}
            </span>
          </div>
          <div class="info-item">
            <label>风险分数</label>
            <span class="risk-score-text">
              {{ ((assessmentInfo.overall_risk?.score || 0) * 100).toFixed(1) }}分
            </span>
          </div>
          <div class="info-item">
            <label>风险百分位</label>
            <span>{{ assessmentInfo.overall_risk?.percentile || 0 }}%</span>
          </div>
        </div>
      </ElCard>

      <!-- 风险评估结果 -->
      <ElCard v-if="assessmentInfo" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a1;</i>
            <span>风险评估结果</span>
          </div>
        </template>
        <div class="risk-overview">
          <div class="gauge-container">
            <RiskGaugeChart
              :value="(assessmentInfo.overall_risk?.score || 0) * 100"
              :level="assessmentInfo.overall_risk?.level || '未知'"
            />
          </div>
          <div class="risk-details">
            <div class="risk-item highlight">
              <label>综合风险等级</label>
              <span
                class="risk-level-badge"
                :style="{ backgroundColor: getRiskColor(assessmentInfo.overall_risk?.level || '') }"
              >
                {{ assessmentInfo.overall_risk?.level || '未知' }}
              </span>
            </div>
            <div class="risk-item">
              <label>风险分数</label>
              <span class="risk-score">
                {{ ((assessmentInfo.overall_risk?.score || 0) * 100).toFixed(1) }} 分
              </span>
            </div>
            <div class="risk-item">
              <label>风险百分位</label>
              <span> 比 {{ assessmentInfo.overall_risk?.percentile || 0 }}% 的同龄人风险更高 </span>
            </div>
            <div class="risk-item">
              <label>推理耗时</label>
              <span>{{ assessmentInfo.inference_time_ms || 0 }}ms</span>
            </div>
          </div>
        </div>

        <!-- 分类风险 -->
        <div v-if="categoryRisks.length > 0" class="category-risks">
          <h4>各类肿瘤风险分析</h4>
          <div class="category-grid">
            <div v-for="item in categoryRisks" :key="item.name" class="category-card">
              <div class="category-header">
                <span class="category-name">{{ item.name }}</span>
                <ElTag :type="getRiskTagType(item.level)" size="small">
                  {{ item.level }}
                </ElTag>
              </div>
              <ElProgress
                :percentage="item.score"
                :color="getProgressColor(item.score)"
                :stroke-width="10"
              />
              <span class="category-score">{{ item.score.toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </ElCard>

      <!-- 关键风险因素 -->
      <ElCard v-if="keyFactors.length > 0" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a3;</i>
            <span>关键风险因素分析</span>
          </div>
        </template>
        <ShapWaterfallChart :factors="keyFactors" :baseline="50" />
        <div class="factors-list">
          <div v-for="(factor, index) in keyFactors" :key="index" class="factor-item">
            <div class="factor-icon" :class="factor.direction">
              <i
                class="iconfont-sys"
                v-html="factor.direction === 'increase' ? '&#xe7b1;' : '&#xe7b2;'"
              ></i>
            </div>
            <div class="factor-content">
              <div class="factor-name">{{ factor.factor }}</div>
              <div class="factor-desc">{{ factor.description }}</div>
            </div>
            <div class="factor-value" :class="factor.direction">
              {{ factor.direction === 'increase' ? '+' : ''
              }}{{ (factor.contribution * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
      </ElCard>

      <!-- 特征重要性 -->
      <ElCard v-if="featureImportance.length > 0" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a5;</i>
            <span>特征重要性分析</span>
          </div>
        </template>
        <FeatureImportanceChart :features="featureImportance" :display-count="15" />
      </ElCard>

      <!-- 模型性能信息 -->
      <ElCard v-if="modelInfo" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a0;</i>
            <span>模型性能指标</span>
          </div>
        </template>
        <ModelPerformanceBadge :model-info="modelInfo" />
      </ElCard>

      <!-- 健康建议 -->
      <ElCard v-if="recommendations.length > 0" class="detail-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe86e;</i>
            <span>个性化健康建议</span>
          </div>
        </template>
        <div class="recommendations-list">
          <div
            v-for="(rec, index) in recommendations"
            :key="index"
            class="recommendation-item"
            :class="`priority-${rec.priority}`"
          >
            <div class="rec-icon">
              <i class="iconfont-sys" v-html="getCategoryIcon(rec.category)"></i>
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.content }}</p>
            </div>
            <div v-if="rec.priority === 1" class="rec-badge">
              <ElTag type="danger" size="small">重要</ElTag>
            </div>
          </div>
        </div>
      </ElCard>

      <!-- AI生成建议 -->
      <ElCard v-if="aiRecommendation" class="detail-card ai-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys" style="color: #67c23a">&#xe7a0;</i>
            <span>🤖 AI个性化建议</span>
            <ElTag type="success" size="small" effect="dark">GLM-4.6</ElTag>
          </div>
        </template>
        <div class="ai-content">
          {{ aiRecommendation }}
        </div>
      </ElCard>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import RiskGaugeChart from '@/components/custom/risk-gauge-chart.vue'
  import ShapWaterfallChart from '@/components/custom/shap-waterfall-chart.vue'
  import FeatureImportanceChart from '@/components/custom/feature-importance-chart.vue'
  import ModelPerformanceBadge from '@/components/custom/model-performance-badge.vue'
  import { fetchScreeningRecord } from '@/api/screening-records'

  const route = useRoute()
  const router = useRouter()

  const loading = ref(true)

  const recordId = computed(() => route.params.id as string)

  // 详情数据
  const detailData = ref<any>({
    user: {
      id: '',
      nickname: '',
      email: '',
      phone: '',
      status: '',
      created_at: ''
    }
  })

  // 评估信息（来自 assessment 对象）
  const assessmentInfo = ref<any>(null)

  // 分类风险
  const categoryRisks = ref<any[]>([])

  // 关键因素
  const keyFactors = ref<any[]>([])

  // 特征重要性
  const featureImportance = ref<any[]>([])

  // 模型信息
  const modelInfo = ref<any>(null)

  // 健康建议
  const recommendations = ref<any[]>([])

  // AI建议
  const aiRecommendation = ref('')

  // 填充数据的辅助函数
  const fillDetailData = (response: any) => {
    // 填充用户信息
    detailData.value = {
      user: {
        id: response.user_id || response.user?.id || '',
        nickname: response.user_nickname || response.user?.nickname || '',
        email: response.user_email || response.user?.email || '',
        phone: response.user?.phone || '',
        status: response.user?.status || '',
        created_at: response.user?.created_at || response.created_at || ''
      }
    }

    // 填充评估信息（来自 assessment 对象）
    assessmentInfo.value = response.assessment || {
      id: response.id || '',
      created_at: response.created_at || '',
      model_version: response.model_version || '',
      inference_time_ms: response.inference_time_ms || 0,
      overall_risk: response.overall_risk || response.assessment?.overall_risk || null
    }

    // 分类风险
    const categoryRisksData =
      response.assessment?.category_risks ||
      response.category_risks ||
      response.assessment_result?.category_risks

    if (categoryRisksData) {
      categoryRisks.value = Object.entries(categoryRisksData).map(
        ([name, data]: [string, any]) => ({
          name,
          score: data.score * 100,
          level: data.level
        })
      )
    }

    // 关键因素
    keyFactors.value =
      response.assessment?.key_factors ||
      response.key_factors ||
      response.assessment_result?.key_factors ||
      []

    // 特征重要性
    featureImportance.value = response.feature_importance || []

    // 模型信息
    modelInfo.value = response.model_info || null

    // 健康建议
    recommendations.value =
      response.assessment?.recommendations ||
      response.recommendations ||
      response.assessment_result?.recommendations ||
      []

    // AI建议
    aiRecommendation.value =
      response.assessment?.ai_recommendation ||
      response.ai_recommendation ||
      response.assessment_result?.ai_recommendation ||
      ''
  }

  // 加载数据
  onMounted(async () => {
    try {
      loading.value = true

      // 🎯 优先从 state 中获取数据（列表页传递过来的）
      const stateData = (history.state as any)?.recordData

      console.log('📋 管理端筛查记录详情')
      console.log('  - Record ID:', recordId.value)
      console.log(
        '  - 数据来源:',
        stateData ? 'state传递（无需请求API）' : 'params参数（需要请求API）'
      )

      if (stateData) {
        // 使用传递过来的数据（无需请求API）
        console.log('✅ 使用列表页传递的数据:', stateData)
        fillDetailData(stateData)
      } else {
        // 降级方案：从 API 加载（例如用户直接访问详情页链接）
        console.log('⚠️ 未检测到传递的数据，从API加载...')
        const response = (await fetchScreeningRecord(recordId.value)) as any
        console.log('✅ API数据加载成功:', response)
        fillDetailData(response)
      }
    } catch (error) {
      console.error('❌ 加载筛查记录详情失败:', error)
      ElMessage.error('加载详情失败')
    } finally {
      loading.value = false
    }
  })

  // 返回列表
  const goBack = () => {
    router.push('/system/screening-records')
  }

  // 辅助函数
  const getRiskColor = (level: string): string => {
    const colorMap: Record<string, string> = {
      低风险: '#52c41a',
      中风险: '#faad14',
      高风险: '#fa8c16',
      极高风险: '#f5222d'
    }
    return colorMap[level] || '#999'
  }

  const getRiskTagType = (level: string) => {
    const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
      低风险: 'success',
      中风险: 'warning',
      高风险: 'danger',
      极高风险: 'danger'
    }
    return typeMap[level] || 'info'
  }

  const getProgressColor = (value: number): string => {
    if (value < 40) return '#52c41a'
    if (value < 60) return '#faad14'
    if (value < 80) return '#fa8c16'
    return '#f5222d'
  }

  const getCategoryIcon = (category: string): string => {
    const iconMap: Record<string, string> = {
      lifestyle: '&#xe7b5;',
      diet: '&#xe7b6;',
      screening: '&#xe7b7;',
      medical: '&#xe7b8;'
    }
    return iconMap[category] || '&#xe86e;'
  }
</script>

<style scoped lang="scss">
  .screening-detail-container {
    max-width: 1400px;
    padding: 20px;
    margin: 0 auto;

    .detail-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px;
      margin-bottom: 24px;
      background: var(--art-main-bg-color);
      border-radius: 8px;
      box-shadow: 0 2px 8px rgb(0 0 0 / 6%);

      .header-left {
        display: flex;
        gap: 15px;
        align-items: center;

        .iconfont-sys {
          font-size: 40px;
          color: var(--el-color-primary);
        }

        .header-text {
          h1 {
            margin: 0 0 5px;
            font-size: 24px;
            font-weight: 600;
            color: var(--art-text-gray-800);
          }

          p {
            margin: 0;
            font-size: 13px;
            color: var(--art-text-gray-500);
          }
        }
      }

      .header-actions {
        display: flex;
        gap: 10px;

        .iconfont-sys {
          margin-right: 4px;
        }
      }
    }

    .detail-content {
      min-height: 400px;
    }

    .detail-card {
      margin-bottom: 20px;

      .card-header {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 18px;
        font-weight: 600;
        color: var(--art-text-gray-800);

        .iconfont-sys {
          font-size: 20px;
          color: var(--el-color-primary);
        }

        .arrow {
          font-size: 14px;
          transition: transform 0.3s;

          &.rotate {
            transform: rotate(90deg);
          }
        }
      }
    }

    // 用户信息网格
    .user-info-grid,
    .assessment-info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;

      .info-item {
        display: flex;
        flex-direction: column;
        gap: 8px;

        label {
          font-size: 13px;
          font-weight: 500;
          color: var(--art-text-gray-500);
        }

        span {
          font-size: 15px;
          color: var(--art-text-gray-800);
        }

        .risk-level-text {
          font-size: 16px;
          font-weight: 600;
        }

        .risk-score-text {
          font-size: 18px;
          font-weight: 600;
          color: var(--el-color-primary);
        }
      }
    }

    // 风险总览
    .risk-overview {
      display: flex;
      gap: 40px;
      align-items: center;
      margin-bottom: 30px;

      .gauge-container {
        flex: 1;
      }

      .risk-details {
        display: flex;
        flex: 1;
        flex-direction: column;
        gap: 20px;

        .risk-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: var(--art-bg-gray-50);
          border-radius: 6px;

          &.highlight {
            background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
          }

          label {
            font-size: 14px;
            font-weight: 500;
            color: var(--art-text-gray-600);
          }

          span {
            font-size: 15px;
            font-weight: 600;
            color: var(--art-text-gray-800);
          }

          .risk-level-badge {
            padding: 6px 16px;
            font-size: 16px;
            font-weight: bold;
            color: white;
            border-radius: 20px;
          }

          .risk-score {
            font-size: 20px;
            color: var(--el-color-primary);
          }
        }
      }
    }

    // 分类风险
    .category-risks {
      padding-top: 30px;
      margin-top: 30px;
      border-top: 1px solid var(--el-border-color-light);

      h4 {
        margin: 0 0 20px;
        font-size: 16px;
        font-weight: 600;
        color: var(--art-text-gray-800);
      }

      .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;

        .category-card {
          padding: 16px;
          background: var(--art-bg-gray-50);
          border-radius: 8px;

          .category-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;

            .category-name {
              font-size: 14px;
              font-weight: 600;
              color: var(--art-text-gray-700);
            }
          }

          .category-score {
            display: block;
            margin-top: 8px;
            font-size: 13px;
            color: var(--art-text-gray-500);
            text-align: right;
          }
        }
      }
    }

    // 关键因素列表
    .factors-list {
      margin-top: 20px;

      .factor-item {
        display: flex;
        gap: 15px;
        align-items: center;
        padding: 16px;
        margin-bottom: 12px;
        background: var(--art-bg-gray-50);
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: var(--art-bg-gray-100);
          box-shadow: 0 2px 8px rgb(0 0 0 / 6%);
        }

        .factor-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          border-radius: 50%;

          &.increase {
            color: #fa8c16;
            background: #fff2e8;
          }

          &.decrease {
            color: #52c41a;
            background: #f6ffed;
          }

          .iconfont-sys {
            font-size: 18px;
          }
        }

        .factor-content {
          flex: 1;

          .factor-name {
            margin-bottom: 4px;
            font-size: 15px;
            font-weight: 600;
            color: var(--art-text-gray-800);
          }

          .factor-desc {
            font-size: 13px;
            color: var(--art-text-gray-500);
          }
        }

        .factor-value {
          font-size: 18px;
          font-weight: bold;

          &.increase {
            color: #fa8c16;
          }

          &.decrease {
            color: #52c41a;
          }
        }
      }
    }

    // 健康建议
    .recommendations-list {
      .recommendation-item {
        display: flex;
        gap: 15px;
        align-items: flex-start;
        padding: 16px;
        margin-bottom: 12px;
        background: var(--art-bg-gray-50);
        border-left: 4px solid var(--el-color-info);
        border-radius: 6px;

        &.priority-1 {
          background: #fff7e6;
          border-left-color: var(--el-color-danger);
        }

        .rec-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          background: white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgb(0 0 0 / 6%);

          .iconfont-sys {
            font-size: 20px;
            color: var(--el-color-primary);
          }
        }

        .rec-content {
          flex: 1;

          h4 {
            margin: 0 0 8px;
            font-size: 15px;
            font-weight: 600;
            color: var(--art-text-gray-800);
          }

          p {
            margin: 0;
            font-size: 14px;
            line-height: 1.6;
            color: var(--art-text-gray-600);
          }
        }

        .rec-badge {
          flex-shrink: 0;
        }
      }
    }

    // AI建议卡片
    .ai-card {
      border: 2px solid #67c23a;

      .ai-content {
        padding: 20px;
        font-size: 15px;
        line-height: 1.8;
        color: var(--art-text-gray-800);
        word-wrap: break-word;
        white-space: pre-wrap;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 8px;
      }
    }

    // 原始数据
    .raw-data-card {
      .raw-data-content {
        max-height: 600px;
        overflow: auto;

        pre {
          padding: 16px;
          margin: 0;
          font-family: 'Courier New', monospace;
          font-size: 12px;
          line-height: 1.5;
          color: var(--art-text-gray-700);
          background: #f6f6f6;
          border-radius: 6px;
        }
      }
    }

    // 响应式
    @media (width <= 768px) {
      padding: 10px;

      .detail-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;

        .header-actions {
          flex-wrap: wrap;
          width: 100%;

          .el-button {
            flex: 1;
          }
        }
      }

      .risk-overview {
        flex-direction: column;

        .gauge-container,
        .risk-details {
          width: 100%;
        }
      }

      .user-info-grid {
        grid-template-columns: 1fr;
      }

      .category-grid {
        grid-template-columns: 1fr !important;
      }
    }
  }
</style>
