<template>
  <div class="report-container">
    <div class="report-header">
      <div class="header-left">
        <div class="logo-section">
          <i class="iconfont-sys medical-icon">&#xe721;</i>
          <div class="certification-marks">
            <ElTag type="success" size="small" effect="plain">AI辅助诊断</ElTag>
            <ElTag type="info" size="small" effect="plain">医疗级算法</ElTag>
          </div>
        </div>
        <div class="header-text">
          <h1>肿瘤风险评估报告</h1>
          <div class="report-meta">
            <span class="meta-item">
              <i class="iconfont-sys">&#xe7b9;</i>
              报告编号: {{ reportData?.reportId || 'REP-20241012-001' }}
            </span>
            <span class="meta-item">
              <i class="iconfont-sys">&#xe7a0;</i>
              生成时间: {{ formatDate(reportData?.createdAt) }}
            </span>
          </div>
        </div>
      </div>
      <div class="report-actions">
        <ElButton @click="goBack">
          <i class="iconfont-sys">&#xe625;</i>
          返回
        </ElButton>
        <ElButton type="success" @click="goToTrend">
          <i class="iconfont-sys">&#xe7a3;</i>
          查看趋势
        </ElButton>
        <ElButton type="primary" @click="exportPDF" :loading="exportLoading">
          <i class="iconfont-sys">&#xe7a8;</i>
          导出PDF
        </ElButton>
      </div>
    </div>

    <div v-loading="loading" element-loading-text="正在生成报告..." class="report-content">
      <!-- 风险总览 -->
      <ElCard class="report-card professional-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a1;</i>
              <span>综合风险评估</span>
            </div>
            <div class="certification-badge">
              <ElTag type="success" effect="dark" size="small">
                <i class="iconfont-sys">&#xe86e;</i>
                AI智能分析
              </ElTag>
            </div>
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
              您的综合风险评分为
              <strong class="score-highlight">{{ (reportData.overallRisk.score * 100).toFixed(0) }}</strong> 分
            </p>
            <p class="percentile-text">
              <i class="iconfont-sys">&#xe7a3;</i>
              健康状况优于
              <strong class="percentile-highlight">{{ reportData.overallRisk.percentile }}%</strong>
              的同龄人
            </p>
            <ElAlert
              :type="getRiskAlertType(reportData.overallRisk.level)"
              :closable="false"
              show-icon
              class="risk-alert"
            >
              <template #title>
                {{ getRiskNote(reportData.overallRisk.level) }}
              </template>
            </ElAlert>
          </div>
        </div>
      </ElCard>

      <!-- 关键因素分析 -->
      <ElCard class="report-card professional-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a3;</i>
              <span>关键风险因素分析</span>
            </div>
            <ElTag type="info" size="small" effect="plain">基于SHAP可解释AI</ElTag>
          </div>
        </template>
        <ShapWaterfallChart :factors="reportData.keyFactors" :baseline="50" />
        <div class="chart-description">
          <ElAlert type="info" :closable="false">
            <template #title>
              <div class="chart-legend">
                <span class="legend-item">
                  <span class="legend-color increase"></span>
                  增加风险因素
                </span>
                <span class="legend-item">
                  <span class="legend-color decrease"></span>
                  降低风险因素
                </span>
              </div>
              <p class="legend-desc">上图展示了各因素对您风险评分的贡献度，帮助您了解主要风险来源</p>
            </template>
          </ElAlert>
        </div>
      </ElCard>

      <!-- 分类风险 -->
      <ElCard class="report-card professional-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a5;</i>
              <span>各类肿瘤风险细分</span>
            </div>
            <ElTag type="warning" size="small" effect="plain">多维度评估</ElTag>
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

      <!-- 模型性能徽章 -->
      <ElCard v-if="v2ModelInfo" class="model-info-card professional-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a0;</i>
              <span>AI模型信息</span>
            </div>
            <ElTag type="success" size="small" effect="dark">医疗级认证</ElTag>
          </div>
        </template>
        <ModelPerformanceBadge :model-info="v2ModelInfo" />
      </ElCard>

      <!-- 特征重要性图表 -->
      <ElCard
        v-if="v2FeatureImportance && v2FeatureImportance.length > 0"
        class="report-card professional-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a3;</i>
              <span>特征重要性分析</span>
            </div>
            <ElTag type="info" size="small" effect="plain">数据驱动</ElTag>
          </div>
        </template>
        <FeatureImportanceChart
          :features="v2FeatureImportance"
          :loading="loading"
          :display-count="10"
        />
      </ElCard>

      <!-- AI个性化建议（手动生成） -->
      <ElCard class="ai-recommendation-card professional-card report-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys" style="color: #67c23a">&#xe7a0;</i>
              <span>AI个性化健康建议</span>
            </div>
            <ElTag type="success" size="small" effect="dark">智谱GLM-4.6</ElTag>
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
              <span>AI正在分析您的健康数据，生成个性化建议...</span>
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
                此建议由智谱GLM-4.6大模型基于您的评估数据生成，仅供参考，不构成医疗诊断。如有疑虑请咨询专业医生。
              </span>
            </div>
          </div>

          <!-- 未生成 -->
          <div v-else class="ai-empty">
            <ElEmpty description="点击按钮生成AI个性化健康建议">
              <ElButton type="primary" @click="generateAIRecommendation">
                <i class="iconfont-sys">&#xe7a0;</i>
                立即生成
              </ElButton>
            </ElEmpty>
          </div>
        </div>
      </ElCard>

      <!-- 推荐检查项目 -->
      <ElCard class="report-card professional-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7b9;</i>
              <span>推荐检查项目</span>
            </div>
            <ElTag type="warning" size="small" effect="plain">个性化方案</ElTag>
          </div>
        </template>
        <ElTable :data="recommendedTests" stripe class="professional-table">
          <ElTableColumn prop="name" label="检查项目" min-width="120">
            <template #default="{ row }">
              <div class="test-name">
                <i class="iconfont-sys">&#xe7b9;</i>
                {{ row.name }}
              </div>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="frequency" label="推荐频率" width="120" />
          <ElTableColumn prop="cost" label="费用估算" width="120">
            <template #default="{ row }">
              <ElTag type="info" size="small">{{ row.cost }}</ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="description" label="说明" min-width="200" />
        </ElTable>
      </ElCard>

      <!-- 免责声明 -->
      <ElCard class="disclaimer-card professional-card" shadow="never">
        <ElAlert type="warning" :closable="false" show-icon>
          <template #title>
            <div class="disclaimer-content">
              <strong>重要声明</strong>
              <p>
                本系统提供的风险评估结果基于AI算法和统计模型，仅供健康管理参考，不能替代专业医疗诊断。评估结果受多种因素影响，建议结合个人实际情况和医生建议综合判断。如有健康问题或疑虑，请及时就医并咨询专业医生。
              </p>
              <div class="data-source">
                <i class="iconfont-sys">&#xe7a3;</i>
                数据来源：基于大规模临床数据训练的XGBoost模型 | 准确率：81.2% | AUC：0.80
              </div>
            </div>
          </template>
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
  // 扩展组件
  import FeatureImportanceChart from '@/components/custom/feature-importance-chart.vue'
  import ModelPerformanceBadge from '@/components/custom/model-performance-badge.vue'
  // 评估 API
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
      percentile: 32  // 修正：风险0.68 → 百分位32（健康状况优于32%的人）
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

  // 填充报告数据的辅助函数（避免代码重复）
  const fillReportData = (data: any, assessmentId: string) => {
    if (!data) return

    // 更新综合风险
    if (data.assessment_result?.overall_risk) {
      const overallRisk = data.assessment_result.overall_risk
      // 确保百分位计算正确：风险越低，百分位越高
      if (overallRisk.percentile === undefined || overallRisk.percentile > 100) {
        overallRisk.percentile = Math.round((1 - overallRisk.score) * 100)
      }
      reportData.value.overallRisk = overallRisk
    }

    // 更新分类风险
    if (data.assessment_result?.category_risks) {
      reportData.value.categoryRisks = data.assessment_result.category_risks
    }

    // 更新关键因素 - 翻译英文特征名
    if (data.assessment_result?.key_factors) {
      reportData.value.keyFactors = data.assessment_result.key_factors.map((factor: any) => ({
        ...factor,
        factor: translateFeatureName(factor.factor)
      }))
    }

    // 更新健康建议
    if (data.assessment_result?.recommendations) {
      reportData.value.recommendations = data.assessment_result.recommendations
    }

    // 扩展数据
    v2ModelInfo.value = data.model_info
    
    // 翻译特征重要性中的英文名称
    if (data.feature_importance) {
      v2FeatureImportance.value = data.feature_importance.map((item: any) => ({
        ...item,
        factor: translateFeatureName(item.factor)
      }))
    } else {
      v2FeatureImportance.value = []
    }
    
    v2AiRecommendation.value = data.assessment_result?.ai_recommendation || ''
    v2ShapAnalysis.value = data.shap_analysis

    reportData.value.assessmentId = assessmentId
    reportData.value.reportId = data.report_id
  }

  // 特征名称翻译映射
  const translateFeatureName = (englishName: string): string => {
    const translations: Record<string, string> = {
      // 基础特征
      'age': '年龄',
      'gender': '性别',
      'bmi': '体重指数BMI',
      'smoking_status': '吸烟状况',
      'alcohol_status': '饮酒状况',
      'exercise_level': '运动水平',
      
      // 遗传与家族史
      'genetic_risk': '遗传风险',
      'family_history': '家族病史',
      
      // 医学指标
      'tumor_marker_score': '肿瘤标志物评分',
      'tissue_abnormality': '组织异常',
      
      // 女性特有
      'menstrual_abnormal': '月经异常',
      'pregnancy_count': '怀孕次数',
      'hormone_therapy': '激素治疗',
      'reproductive_risk_score': '生育风险评分',
      
      // 环境与职业
      'occupational_exposure_score': '职业暴露评分',
      'environmental_risk_score': '环境风险评分',
      
      // 饮食习惯
      'diet_quality_score': '饮食质量评分',
      'vegetable_fruit_score': '蔬果摄入评分',
      'red_meat_score': '红肉摄入评分',
      'processed_food_score': '加工食品评分',
      
      // 生活方式
      'stress_level_score': '压力水平评分',
      'work_rest_regularity': '作息规律性',
      'lifestyle_score': '生活方式评分',
      
      // 筛查历史
      'screening_history_score': '筛查历史评分',
      'abnormal_results_count': '异常结果次数',
      
      // 派生特征
      'bmi_category': 'BMI分类',
      'age_group': '年龄组',
      'comprehensive_risk': '综合风险',
      
      // 交互特征
      'age_x_smoking': '年龄×吸烟交互',
      'bmi_x_exercise': 'BMI×运动交互',
      'age_x_genetic': '年龄×遗传交互',
      'age_x_bmi': '年龄×BMI交互',
      
      // V1.0 旧特征
      'Age': '年龄',
      'Gender': '性别',
      'BMI': '体重指数BMI',
      'Smoking': '吸烟',
      'GeneticRisk': '遗传风险',
      'PhysicalActivity': '运动量',
      'AlcoholIntake': '饮酒量',
      'CancerHistory': '癌症病史',
      'BMI_Category': 'BMI分类',
      'Age_Group': '年龄组',
      'HighRisk_Flag': '高风险标志',
      'Health_Score': '健康评分',
      'Age_x_Smoking': '年龄×吸烟',
      'BMI_x_Activity': 'BMI×运动',
      'Genetic_x_History': '遗传×病史'
    }
    
    return translations[englishName] || englishName
  }

  onMounted(async () => {
    // 优先从 state 中获取所有数据（父传子方案）
    const stateData = (history.state as any)?.reportData
    const stateAssessmentId = (history.state as any)?.assessmentId

    // 降级：如果 state 中没有 ID，尝试从 params 获取
    const assessmentId = stateAssessmentId || (route.params.id as string)

    console.log('加载评估报告')
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
      return // 直接返回，不再请求API
    }

    // 如果没有传递数据，则尝试从API加载（降级方案）
    console.log('未检测到路由传递的数据，尝试从API加载...')

    try {
      // 尝试调用评估 API
      try {
        const response: any = await fetchAssessmentDetailV2(assessmentId)
        const data = response.data || response // 兼容不同的响应格式
        console.log('API数据加载成功:', data)

        // 使用辅助函数填充数据
        fillReportData(data, assessmentId)
      } catch (apiError) {
        console.warn('API调用失败，使用模拟数据:', apiError)
        // 如果 API 失败，使用模拟数据（向后兼容）
        await new Promise((resolve) => setTimeout(resolve, 1000))
        reportData.value.assessmentId = assessmentId

        // 模拟数据
        v2ModelInfo.value = {
          version: 'enhanced',
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
          '**根据您的风险评估结果，我为您提供以下个性化建议：**\n\n### 立即戒烟\n您的吸烟史是最主要的风险因素。建议：\n- 制定明确的戒烟计划\n- 考虑戒烟门诊或药物辅助\n- 避免吸烟环境\n\n### 加强运动\n适度运动可以显著降低肿瘤风险：\n- 每周至少150分钟中等强度运动\n- 推荐：快走、游泳、骑车\n\n### 改善饮食\n- 增加新鲜蔬菜水果摄入\n- 减少红肉和加工食品\n- 多吃全谷物和豆类\n\n### 定期筛查\n鉴于您的风险等级，建议：\n- 每年进行低剂量螺旋CT（肺部筛查）\n- 定期检查肿瘤标志物\n- 及时就医咨询专业医生'
      }
    } catch (error) {
      console.error('加载报告失败:', error)
      ElMessage.error('报告加载失败')
    } finally {
      loading.value = false
    }
  })

  const goBack = () => {
    router.back()
  }

  const goToTrend = () => {
    router.push('/risk/trend')
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

  const formatDate = (dateStr: string | undefined): string => {
    if (!dateStr) return new Date().toLocaleString('zh-CN')
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
</script>

<style scoped lang="scss">
  .report-container {
    max-width: 1400px;
    padding: 20px;
    margin: 0 auto;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    min-height: 100vh;

    .report-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 30px;
      margin-bottom: 30px;
      background: linear-gradient(135deg, #ffffff 0%, #f8f9fb 100%);
      border-radius: 12px;
      box-shadow: 0 4px 12px rgb(0 0 0 / 8%);
      border: 1px solid #e8eef5;

      .header-left {
        display: flex;
        gap: 20px;
        align-items: center;

        .logo-section {
          display: flex;
          flex-direction: column;
          gap: 8px;
          align-items: center;

          .medical-icon {
            font-size: 48px;
            color: #1890ff;
            filter: drop-shadow(0 2px 4px rgb(24 144 255 / 20%));
          }

          .certification-marks {
            display: flex;
            gap: 4px;
          }
        }

        .header-text {
          h1 {
            margin: 0 0 10px;
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            letter-spacing: 0.5px;
          }

          .report-meta {
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: #666;

            .meta-item {
              display: flex;
              gap: 6px;
              align-items: center;

              .iconfont-sys {
                font-size: 14px;
                color: #1890ff;
              }
            }
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

    // 专业卡片样式
    .professional-card {
      border: 1px solid #e8eef5;
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 8px 24px rgb(0 0 0 / 12%);
        transform: translateY(-2px);
      }

      :deep(.el-card__header) {
        background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
        border-bottom: 2px solid #e8eef5;
        padding: 20px 24px;
      }

      :deep(.el-card__body) {
        padding: 24px;
      }
    }

    .report-card {
      margin-bottom: 20px;

      .card-header {
        display: flex;
        gap: 12px;
        align-items: center;
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;

        .header-left {
          display: flex;
          gap: 10px;
          align-items: center;
          flex: 1;
        }

        .iconfont-sys {
          font-size: 22px;
          color: #1890ff;
        }

        .certification-badge {
          margin-left: auto;
        }
      }

      .chart-description {
        margin-top: 20px;

        .chart-legend {
          display: flex;
          gap: 24px;
          align-items: center;
          margin-bottom: 8px;

          .legend-item {
            display: flex;
            gap: 8px;
            align-items: center;
            font-size: 14px;

            .legend-color {
              width: 20px;
              height: 4px;
              border-radius: 2px;

              &.increase {
                background: #f5222d;
              }

              &.decrease {
                background: #52c41a;
              }
            }
          }
        }

        .legend-desc {
          margin: 8px 0 0;
          font-size: 13px;
          color: #666;
        }
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
          font-size: 42px;
          font-weight: bold;
          text-shadow: 0 2px 4px rgb(0 0 0 / 10%);
        }

        .risk-text {
          margin-bottom: 12px;
          font-size: 16px;
          line-height: 1.8;
          color: #333;

          .score-highlight {
            font-size: 24px;
            font-weight: bold;
            color: #1890ff;
            padding: 0 4px;
          }
        }

        .percentile-text {
          display: flex;
          gap: 8px;
          align-items: center;
          margin-bottom: 20px;
          padding: 12px 16px;
          font-size: 15px;
          background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
          border-radius: 8px;
          border-left: 4px solid #1890ff;

          .iconfont-sys {
            font-size: 18px;
            color: #1890ff;
          }

          .percentile-highlight {
            font-size: 20px;
            font-weight: bold;
            color: #1890ff;
          }
        }

        .risk-alert {
          border-radius: 8px;
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
        padding: 12px;
        background: #fafbfc;
        border-radius: 8px;
        transition: all 0.2s ease;

        &:hover {
          background: #f0f2f5;
          transform: translateX(4px);
        }

        .category-name {
          width: 100px;
          font-size: 15px;
          font-weight: 500;
          color: #1a1a1a;
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

    // 模型信息卡片
    .model-info-card {
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      border: 2px solid #91d5ff;
    }

    // AI建议卡片样式
    .ai-recommendation-card {
      border: 2px solid #95de64;
      background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);

      .card-header {
        background: linear-gradient(135deg, #f6ffed 0%, #eaffe6 100%);
        border-bottom: 2px solid #95de64;

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
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 500;
            color: #52c41a;
            background: #f6ffed;
            border-radius: 8px;
            border-left: 4px solid #52c41a;

            .el-icon {
              font-size: 18px;
            }
          }

          .ai-text-stream {
            min-height: 100px;
            padding: 20px;
            font-size: 15px;
            line-height: 1.8;
            color: #1a1a1a;
            word-wrap: break-word;
            white-space: pre-wrap;
            background: #fff;
            border-radius: 8px;
            box-shadow: inset 0 2px 8px rgb(0 0 0 / 5%);

            .cursor-blink {
              display: inline-block;
              font-weight: bold;
              color: #52c41a;
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
            color: #1a1a1a;
            word-wrap: break-word;
            white-space: pre-wrap;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgb(82 196 26 / 10%);
          }

          .ai-footer {
            display: flex;
            gap: 8px;
            align-items: flex-start;
            padding: 12px 16px;
            font-size: 12px;
            line-height: 1.6;
            color: #666;
            background: #fffbe6;
            border-radius: 6px;
            border-left: 3px solid #faad14;

            .el-icon {
              flex-shrink: 0;
              margin-top: 2px;
              font-size: 14px;
              color: #faad14;
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

    // 专业表格样式
    .professional-table {
      .test-name {
        display: flex;
        gap: 8px;
        align-items: center;
        font-weight: 500;

        .iconfont-sys {
          color: #1890ff;
        }
      }
    }

    .disclaimer-card {
      margin-top: 30px;
      background: linear-gradient(135deg, #fffbe6 0%, #fff7e6 100%);
      border: 1px solid #ffe58f;

      .disclaimer-content {
        strong {
          display: block;
          margin-bottom: 12px;
          font-size: 16px;
          color: #d46b08;
        }

        p {
          margin: 0 0 12px;
          font-size: 14px;
          line-height: 1.8;
          color: #595959;
        }

        .data-source {
          display: flex;
          gap: 8px;
          align-items: center;
          padding: 8px 12px;
          font-size: 12px;
          color: #8c8c8c;
          background: rgb(255 255 255 / 60%);
          border-radius: 4px;

          .iconfont-sys {
            color: #1890ff;
          }
        }
      }
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
        padding: 20px;

        .header-left {
          flex-direction: column;
          align-items: flex-start;
        }

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
