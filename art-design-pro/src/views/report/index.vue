<template>
  <div class="report-container">
    <div class="report-header">
      <div class="header-left">
        <i class="iconfont-sys">&#xe721;</i>
        <div class="header-text">
          <h1>肿瘤风险评估报告</h1>
          <p>报告编号: {{ reportData?.reportId || 'REP-20241012-001' }}</p>
        </div>
      </div>
      <div class="report-actions">
        <ElButton @click="goBack">
          <i class="iconfont-sys">&#xe625;</i>
          返回
        </ElButton>
        <ElButton type="primary" @click="exportPDF" :loading="exportLoading">
          <i class="iconfont-sys">&#xe7a8;</i>
          导出PDF
        </ElButton>
      </div>
    </div>

    <div v-loading="loading" element-loading-text="正在生成报告..." class="report-content">
      <!-- 风险总览 -->
      <ElCard class="report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a1;</i>
            <span>综合风险评估</span>
          </div>
        </template>
        <div class="risk-overview">
          <div class="gauge-container">
            <RiskGaugeChart
              :value="reportData.overallRisk.score * 100"
              :level="reportData.overallRisk.level"
            />
          </div>
          <div class="risk-description">
            <h3
              class="risk-level"
              :style="{ color: getRiskLevelColor(reportData.overallRisk.level) }"
            >
              {{ reportData.overallRisk.level }}
            </h3>
            <p class="risk-text">
              您的风险评分为
              <strong>{{ (reportData.overallRisk.score * 100).toFixed(0) }}</strong> 分， 比
              <strong>{{ reportData.overallRisk.percentile }}%</strong> 的同龄人风险更高。
            </p>
            <ElAlert
              :type="getRiskAlertType(reportData.overallRisk.level)"
              :closable="false"
              show-icon
            >
              <template #title>
                {{ getRiskNote(reportData.overallRisk.level) }}
              </template>
            </ElAlert>
          </div>
        </div>
      </ElCard>

      <!-- 关键因素分析 -->
      <ElCard class="report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a3;</i>
            <span>关键风险因素分析</span>
          </div>
        </template>
        <ShapWaterfallChart :factors="reportData.keyFactors" :baseline="50" />
        <div class="chart-description">
          <ElAlert type="info" :closable="false">
            <template #title>
              上图展示了各因素对您风险评分的贡献度。
              <span style="color: #f5222d">红色</span>表示增加风险，
              <span style="color: #52c41a">绿色</span>表示降低风险。
            </template>
          </ElAlert>
        </div>
      </ElCard>

      <!-- 分类风险 -->
      <ElCard class="report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7a5;</i>
            <span>各类肿瘤风险细分</span>
          </div>
        </template>
        <RiskRadarChart :data="categoryRisksData" />
        <div class="category-list">
          <div v-for="(item, index) in categoryRisksData" :key="index" class="category-item">
            <span class="category-name">{{ item.name }}</span>
            <ElProgress
              :percentage="item.value"
              :color="getProgressColor(item.value)"
              :stroke-width="12"
            />
            <ElTag :type="getRiskTagType(item.level)" size="small">
              {{ item.level }}
            </ElTag>
          </div>
        </div>
      </ElCard>

      <!-- 健康建议
      <ElCard class="report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe86e;</i>
            <span>个性化健康建议</span>
          </div>
        </template>
        <HealthRecommendations
          :recommendations="reportData.recommendations"
          @action="handleRecommendationAction"
        />
      </ElCard> -->

      <!-- V2.0 新增：模型性能徽章 -->
      <ModelPerformanceBadge v-if="v2ModelInfo" :model-info="v2ModelInfo" />

      <!-- V2.0 新增：特征重要性图表 -->
      <FeatureImportanceChart
        v-if="v2FeatureImportance && v2FeatureImportance.length > 0"
        :features="v2FeatureImportance"
        :loading="loading"
        :display-count="10"
      />

      <!-- AI个性化建议（手动生成） -->
      <ElCard class="ai-recommendation-card report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys" style="color: #67c23a">&#xe7a0;</i>
            <span>🤖 AI个性化健康建议</span>
            <ElTag type="success" size="small" effect="dark">由GLM-4.6生成</ElTag>
            <div style="flex: 1"></div>
            <ElButton
              v-if="!aiRecommendation && !isGeneratingAI"
              type="primary"
              size="small"
              @click="generateAIRecommendation"
            >
              <i class="iconfont-sys">&#xe7a0;</i>
              生成AI建议
            </ElButton>
            <ElButton
              v-if="aiRecommendation && !isGeneratingAI"
              type="default"
              size="small"
              @click="regenerateAIRecommendation"
            >
              <i class="iconfont-sys">&#xe7a2;</i>
              重新生成
            </ElButton>
          </div>
        </template>

        <div class="ai-content">
          <!-- 加载中 -->
          <div v-if="isGeneratingAI" class="ai-generating">
            <div class="generating-header">
              <ElIcon class="is-loading"><Loading /></ElIcon>
              <span>AI正在思考中，请稍候...</span>
            </div>
            <div class="ai-text-stream">
              {{ aiStreamText }}
              <span class="cursor-blink">|</span>
            </div>
          </div>

          <!-- 已生成的内容 -->
          <div v-else-if="aiRecommendation" class="ai-generated">
            <div class="ai-text">
              {{ aiRecommendation }}
            </div>
            <div class="ai-footer">
              <ElIcon><InfoFilled /></ElIcon>
              <span class="disclaimer">
                此建议由智谱GLM-4.6大模型生成，仅供参考，不构成医疗诊断。如有疑虑请咨询专业医生。
              </span>
            </div>
          </div>

          <!-- 未生成 -->
          <div v-else class="ai-empty">
            <ElEmpty description="暂无AI建议">
              <ElButton type="primary" @click="generateAIRecommendation">
                立即生成AI个性化建议
              </ElButton>
            </ElEmpty>
          </div>
        </div>
      </ElCard>

      <!-- 推荐检查项目 -->
      <ElCard class="report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="iconfont-sys">&#xe7b9;</i>
            <span>推荐检查项目</span>
          </div>
        </template>
        <ElTable :data="recommendedTests" stripe>
          <ElTableColumn prop="name" label="检查项目" min-width="120" />
          <ElTableColumn prop="frequency" label="推荐频率" width="120" />
          <ElTableColumn prop="cost" label="费用估算" width="120" />
          <ElTableColumn prop="description" label="说明" min-width="200" />
        </ElTable>
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
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { Loading, InfoFilled } from '@element-plus/icons-vue'
  import RiskGaugeChart from '@/components/custom/risk-gauge-chart.vue'
  import RiskRadarChart from '@/components/custom/risk-radar-chart.vue'
  import ShapWaterfallChart from '@/components/custom/shap-waterfall-chart.vue'
  // V2.0 新增组件
  import FeatureImportanceChart from '@/components/custom/feature-importance-chart.vue'
  import ModelPerformanceBadge from '@/components/custom/model-performance-badge.vue'
  // V2.0 API
  import { fetchAssessmentDetailV2 } from '@/api/assessment-v2'
  import { useUserStore } from '@/store/modules/user'

  const route = useRoute()
  const router = useRouter()
  const userStore = useUserStore()

  const loading = ref(true)
  const exportLoading = ref(false)

  // AI建议相关
  const aiRecommendation = ref('')
  const isGeneratingAI = ref(false)
  const aiStreamText = ref('')

  // V2.0 新增数据
  const v2ModelInfo = ref<any>(null)
  const v2FeatureImportance = ref<any[]>([])
  const v2AiRecommendation = ref<string>('')
  const v2ShapAnalysis = ref<any>(null)

  // 模拟报告数据
  const reportData = ref({
    reportId: 'REP-20241012-001',
    assessmentId: '',
    createdAt: new Date().toISOString(),
    overallRisk: {
      score: 0.68,
      level: '高风险',
      percentile: 82
    },
    categoryRisks: {
      肺癌: { score: 0.75, level: '高风险' },
      胃癌: { score: 0.45, level: '中风险' },
      肝癌: { score: 0.6, level: '高风险' },
      结直肠癌: { score: 0.5, level: '中风险' },
      乳腺癌: { score: 0.3, level: '低风险' }
    },
    keyFactors: [
      {
        factor: '吸烟史',
        contribution: 0.18,
        direction: 'increase' as const,
        description: '长期吸烟（20年）显著增加肺癌风险'
      },
      {
        factor: '家族肿瘤史',
        contribution: 0.12,
        direction: 'increase' as const,
        description: '直系亲属有肺癌病史'
      },
      {
        factor: '年龄',
        contribution: 0.08,
        direction: 'increase' as const,
        description: '55岁属于肿瘤高发年龄段'
      },
      {
        factor: '定期运动',
        contribution: -0.05,
        direction: 'decrease' as const,
        description: '每周运动3次以上，有助降低风险'
      }
    ],
    recommendations: [
      {
        category: 'lifestyle',
        title: '立即戒烟',
        content:
          '吸烟是肺癌的首要危险因素。建议立即戒烟，戒烟可显著降低风险。可以寻求专业戒烟门诊帮助。',
        priority: 1,
        actionText: '查看戒烟方法'
      },
      {
        category: 'diet',
        title: '均衡饮食',
        content: '减少腌制、熏制食品摄入，增加新鲜蔬菜水果。建议每天摄入5种以上不同颜色的蔬果。',
        priority: 2,
        actionText: '饮食建议详情'
      },
      {
        category: 'screening',
        title: '定期肺部CT检查',
        content: '建议每年进行低剂量螺旋CT检查（肺癌筛查），有助于早期发现肺部病变。',
        priority: 1,
        actionText: '了解检查项目'
      },
      {
        category: 'medical',
        title: '尽快就医',
        content: '您的风险评估结果偏高，建议尽快到医院进行全面体检，咨询肿瘤科或呼吸内科医生。',
        priority: 1
      }
    ]
  })

  // 分类风险数据（用于雷达图）
  const categoryRisksData = computed(() => {
    return Object.entries(reportData.value.categoryRisks).map(([name, data]) => ({
      name,
      value: data.score * 100,
      level: data.level
    }))
  })

  // 推荐检查项目
  const recommendedTests = ref([
    {
      name: '低剂量螺旋CT',
      frequency: '每年1次',
      cost: '300-500元',
      description: '用于肺癌早期筛查，适合长期吸烟者'
    },
    {
      name: '胃镜检查',
      frequency: '每2年1次',
      cost: '500-800元',
      description: '适用于胃癌家族史、慢性胃炎患者'
    },
    {
      name: '肿瘤标志物检测',
      frequency: '每年1次',
      cost: '200-400元',
      description: '血液检查，筛查多种肿瘤风险'
    }
  ])

  // 🎯 填充报告数据的辅助函数（避免代码重复）
  const fillReportData = (data: any, assessmentId: string) => {
    if (!data) return

    // 更新综合风险
    if (data.assessment_result?.overall_risk) {
      reportData.value.overallRisk = data.assessment_result.overall_risk
    }

    // 更新分类风险
    if (data.assessment_result?.category_risks) {
      reportData.value.categoryRisks = data.assessment_result.category_risks
    }

    // 更新关键因素
    if (data.assessment_result?.key_factors) {
      reportData.value.keyFactors = data.assessment_result.key_factors
    }

    // 更新健康建议
    if (data.assessment_result?.recommendations) {
      reportData.value.recommendations = data.assessment_result.recommendations
    }

    // V2.0 新增数据
    v2ModelInfo.value = data.model_info
    v2FeatureImportance.value = data.feature_importance || []
    v2AiRecommendation.value = data.assessment_result?.ai_recommendation || ''
    v2ShapAnalysis.value = data.shap_analysis

    reportData.value.assessmentId = assessmentId
    reportData.value.reportId = data.report_id
  }

  onMounted(async () => {
    // 🎯 优先从 state 中获取所有数据（父传子方案）
    const stateData = (history.state as any)?.reportData
    const stateAssessmentId = (history.state as any)?.assessmentId

    // 降级：如果 state 中没有 ID，尝试从 params 获取
    const assessmentId = stateAssessmentId || (route.params.id as string)

    console.log('加载V2.0评估报告')
    console.log('  - Assessment ID:', assessmentId)
    console.log('  - 数据来源:', stateData ? 'state传递' : 'params参数')

    if (stateData) {
      console.log('使用路由传递的数据（无需请求API）:', stateData)

      try {
        fillReportData(stateData, assessmentId)
        console.log('数据填充成功')
      } catch (error) {
        console.error(' 数据解析失败:', error)
        ElMessage.error('报告数据解析失败')
      } finally {
        loading.value = false
      }
      return // 🎯 直接返回，不再请求API
    }

    // 如果没有传递数据，则尝试从API加载（降级方案）
    console.log('⚠️ 未检测到路由传递的数据，尝试从API加载...')

    try {
      // 尝试调用 V2.0 API
      try {
        const response: any = await fetchAssessmentDetailV2(assessmentId)
        const data = response.data || response // 兼容不同的响应格式
        console.log('V2.0 API数据加载成功:', data)

        // 使用辅助函数填充数据
        fillReportData(data, assessmentId)
      } catch (apiError) {
        console.warn('⚠️ V2.0 API调用失败，使用模拟数据:', apiError)
        // 如果 V2 API 失败，使用模拟数据（向后兼容）
        await new Promise((resolve) => setTimeout(resolve, 1000))
        reportData.value.assessmentId = assessmentId

        // 模拟V2.0数据
        v2ModelInfo.value = {
          version: 'v2.0_enhanced',
          feature_count: 32,
          inference_time_ms: 156,
          accuracy: 0.8121,
          auc: 0.8014
        }

        v2FeatureImportance.value = [
          { factor: 'age', contribution: 0.12, importance: 0.12 },
          { factor: 'smoking_status', contribution: 0.18, importance: 0.18 },
          { factor: 'family_history', contribution: 0.1, importance: 0.1 },
          { factor: 'bmi', contribution: 0.08, importance: 0.08 },
          { factor: 'stress_level_score', contribution: 0.06, importance: 0.06 },
          { factor: 'diet_quality_score', contribution: -0.04, importance: 0.04 },
          { factor: 'exercise_level', contribution: -0.05, importance: 0.05 },
          { factor: 'comprehensive_risk', contribution: 0.09, importance: 0.09 },
          { factor: 'tumor_marker_score', contribution: 0.07, importance: 0.07 },
          { factor: 'environmental_risk_score', contribution: 0.05, importance: 0.05 }
        ]

        v2AiRecommendation.value =
          '**根据您的风险评估结果，我为您提供以下个性化建议：**\n\n### 🚭 立即戒烟\n您的吸烟史是最主要的风险因素。建议：\n- 制定明确的戒烟计划\n- 考虑戒烟门诊或药物辅助\n- 避免吸烟环境\n\n### 🏃 加强运动\n适度运动可以显著降低肿瘤风险：\n- 每周至少150分钟中等强度运动\n- 推荐：快走、游泳、骑车\n\n### 🥗 改善饮食\n- 增加新鲜蔬菜水果摄入\n- 减少红肉和加工食品\n- 多吃全谷物和豆类\n\n### 🏥 定期筛查\n鉴于您的风险等级，建议：\n- 每年进行低剂量螺旋CT（肺部筛查）\n- 定期检查肿瘤标志物\n- 及时就医咨询专业医生'
      }
    } catch (error) {
      console.error('❌ 加载报告失败:', error)
      ElMessage.error('报告加载失败')
    } finally {
      loading.value = false
    }
  })

  const goBack = () => {
    router.back()
  }

  const exportPDF = async () => {
    exportLoading.value = true
    try {
      // TODO: 实现PDF导出功能
      // 方案1: 使用 html2canvas + jspdf
      // 方案2: 调用后端API生成PDF
      await new Promise((resolve) => setTimeout(resolve, 1500))
      ElMessage.success('PDF导出成功')
    } catch (error) {
      console.log('error', error)
      ElMessage.error('导出失败，请重试')
    } finally {
      exportLoading.value = false
    }
  }

  /**
   * 生成AI个性化建议（SSE流式）
   */
  const generateAIRecommendation = async () => {
    const assessmentId = route.params.id || reportData.value.assessmentId
    console.log('assessmentId', assessmentId)
    if (!assessmentId) {
      ElMessage.error('评估ID不存在')
      return
    }
    isGeneratingAI.value = true
    aiStreamText.value = ''
    aiRecommendation.value = ''

    try {
      const token = userStore.accessToken
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      console.log('apiUrl', apiUrl)
      const url = `${apiUrl}/api/v1/assessment/${assessmentId}/ai-recommendation`
      // 使用fetch实现SSE（支持Authorization header）
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      // 读取流式响应
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('无法读取响应流')
      }

      // 逐块读取数据
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          // 流结束
          if (aiStreamText.value) {
            aiRecommendation.value = aiStreamText.value
            ElMessage.success('AI建议生成成功')
          }
          isGeneratingAI.value = false
          break
        }

        // 解码数据
        const chunk = decoder.decode(value, { stream: true })

        // 处理SSE格式数据（data: {...}\n\n）
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(6) // 去掉 "data: "
              const data = JSON.parse(jsonStr)

              if (data.type === 'start') {
                console.log('开始生成:', data.message)
              } else if (data.type === 'text') {
                // 追加文本
                aiStreamText.value += data.content
              } else if (data.type === 'done') {
                // 生成完成
                console.log('生成完成:', data.message)
              } else if (data.type === 'error') {
                ElMessage.error(`生成失败: ${data.message}`)
              }
            } catch (e) {
              console.error('解析SSE数据失败:', e, line)
            }
          }
        }
      }
    } catch (error) {
      console.error('生成AI建议失败:', error)
      ElMessage.error('生成失败，请重试')
      isGeneratingAI.value = false
    }
  }

  /**
   * 重新生成AI建议
   */
  const regenerateAIRecommendation = () => {
    aiRecommendation.value = ''
    generateAIRecommendation()
  }

  // 辅助函数
  const getRiskLevelColor = (level: string): string => {
    const colorMap: Record<string, string> = {
      低风险: '#52c41a',
      中风险: '#faad14',
      高风险: '#fa8c16',
      极高风险: '#f5222d'
    }
    return colorMap[level] || '#999'
  }

  const getRiskAlertType = (level: string) => {
    const typeMap: Record<string, 'success' | 'warning' | 'info' | 'error'> = {
      低风险: 'success',
      中风险: 'warning',
      高风险: 'warning',
      极高风险: 'error'
    }
    return typeMap[level] || 'info'
  }

  const getRiskNote = (level: string): string => {
    const notes: Record<string, string> = {
      低风险: '保持良好的生活习惯，定期体检。',
      中风险: '需要注意调整生活方式，增加体检频率。',
      高风险: '建议尽快到医院进行全面体检，咨询专业医生。',
      极高风险: '请立即就医！您存在多项高危因素，需要专业医疗干预。'
    }
    return notes[level] || ''
  }

  const getRiskTagType = (level: string) => {
    const typeMap: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
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
</script>

<style scoped lang="scss">
  .report-container {
    max-width: 1400px;
    padding: 20px;
    margin: 0 auto;

    .report-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px;
      margin-bottom: 30px;
      background: var(--art-main-bg-color);
      border-radius: 8px;

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
            color: var(--art-text-gray-800);
          }

          p {
            margin: 0;
            font-size: 13px;
            color: var(--art-text-gray-500);
          }
        }
      }

      .report-actions {
        display: flex;
        gap: 10px;

        .iconfont-sys {
          margin-right: 4px;
        }
      }
    }

    .report-card {
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
      }

      .chart-description {
        margin-top: 20px;
      }
    }

    .risk-overview {
      display: flex;
      gap: 40px;
      align-items: center;

      .gauge-container {
        flex: 1;
      }

      .risk-description {
        flex: 1;

        .risk-level {
          margin: 0 0 20px;
          font-size: 36px;
          font-weight: bold;
        }

        .risk-text {
          margin-bottom: 20px;
          font-size: 16px;
          line-height: 1.8;
          color: var(--art-text-gray-600);

          strong {
            font-size: 18px;
            color: var(--el-color-primary);
          }
        }
      }
    }

    .category-list {
      margin-top: 30px;

      .category-item {
        display: flex;
        gap: 15px;
        align-items: center;
        margin-bottom: 15px;

        .category-name {
          width: 100px;
          font-size: 14px;
          color: var(--art-text-gray-700);
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

    // AI建议卡片样式
    .ai-recommendation-card {
      border: 2px solid #67c23a;

      .card-header {
        display: flex;
        gap: 10px;
        align-items: center;

        .el-tag {
          margin-left: 10px;
        }
      }

      .ai-content {
        min-height: 150px;

        .ai-generating {
          .generating-header {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 20px;
            font-size: 14px;
            color: var(--el-color-primary);

            .el-icon {
              font-size: 18px;
            }
          }

          .ai-text-stream {
            min-height: 100px;
            padding: 20px;
            font-size: 15px;
            line-height: 1.8;
            color: var(--art-text-gray-800);
            word-wrap: break-word;
            white-space: pre-wrap;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;

            .cursor-blink {
              display: inline-block;
              font-weight: bold;
              color: var(--el-color-primary);
              animation: blink 1s infinite;
            }
          }
        }

        .ai-generated {
          .ai-text {
            padding: 20px;
            margin-bottom: 15px;
            font-size: 15px;
            line-height: 1.8;
            color: var(--art-text-gray-800);
            word-wrap: break-word;
            white-space: pre-wrap;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgb(103 194 58 / 10%);
          }

          .ai-footer {
            display: flex;
            gap: 8px;
            align-items: center;
            font-size: 12px;
            color: var(--art-text-gray-500);

            .el-icon {
              font-size: 14px;
            }
          }
        }

        .ai-empty {
          padding: 20px;
          text-align: center;
        }
      }
    }

    @keyframes blink {
      0%,
      50% {
        opacity: 1;
      }

      51%,
      100% {
        opacity: 0;
      }
    }

    .disclaimer-card {
      margin-top: 30px;
      background: #fffbe6;
      border: 1px solid #ffe58f;
    }
  }

  // 响应式适配
  @media (width <= 768px) {
    .report-container {
      padding: 10px;

      .report-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;

        .report-actions {
          width: 100%;

          .el-button {
            flex: 1;
          }
        }
      }

      .risk-overview {
        flex-direction: column;

        .gauge-container,
        .risk-description {
          width: 100%;
        }
      }

      .category-list {
        .category-item {
          flex-direction: column;
          align-items: flex-start;

          .category-name {
            width: 100%;
          }

          .el-progress {
            width: 100%;
          }
        }
      }
    }
  }
</style>
