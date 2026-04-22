<template>
  <div class="questionnaire-container">
    <!-- Hero 区域 - 带过渡动画 -->
    <Transition name="hero-fade">
      <div v-show="!showQuestionnaire" class="questionnaire-hero">
        <div class="hero-inner">
          <div class="badge-row">
            <span class="dot"></span>
            <span class="badge">增强评估</span>
            <span class="sep">|</span>
            <span class="sub">肿瘤风险智能评估</span>
          </div>

          <h1 class="title-main">健康问卷评估</h1>
          <h2 class="title-sub">从未如此精准</h2>
          <p class="desc">
            基于 XGBoost 机器学习模型，收集 32+ 关键特征，结合 SHAP 可解释性分析与 DeepSeek AI
            智能建议，为您提供专业的肿瘤风险评估报告
          </p>

          <div class="chips">
            <span class="chip">
              <i class="el-icon-check"></i>
              4步完整评估
            </span>
            <span class="chip">
              <i class="el-icon-pie-chart"></i>
              32项关键指标
            </span>
            <span class="chip">
              <i class="el-icon-data-analysis"></i>
              AI个性化建议
            </span>
            <span class="chip">
              <i class="el-icon-trophy"></i>
              准确率81.21%
            </span>
          </div>

          <div class="hero-showcase">
            <div class="showcase-panel mission-panel">
              <div class="panel-eyebrow">项目定位</div>
              <h3>面向院内初筛与患者健康管理的 AI 辅助筛查平台</h3>
              <p>
                通过问卷评估、风险分层、可解释分析与医生协作，形成从患者自测到机构管理的闭环。
              </p>
              <div class="mission-grid">
                <div class="mission-item">
                  <span class="mission-value">4</span>
                  <span class="mission-label">阶段评估流程</span>
                </div>
                <div class="mission-item">
                  <span class="mission-value">32+</span>
                  <span class="mission-label">关键风险特征</span>
                </div>
                <div class="mission-item">
                  <span class="mission-value">SHAP</span>
                  <span class="mission-label">可解释因子拆解</span>
                </div>
              </div>
            </div>
            <div class="showcase-panel architecture-panel">
              <div class="panel-eyebrow">能力闭环</div>
              <div class="flow-list">
                <div class="flow-item">
                  <span class="flow-index">01</span>
                  <div>
                    <strong>智能问卷采集</strong>
                    <p>快速收集生活方式、家族史与近期症状</p>
                  </div>
                </div>
                <div class="flow-item">
                  <span class="flow-index">02</span>
                  <div>
                    <strong>风险建模评估</strong>
                    <p>XGBoost + SHAP 输出风险等级与关键因素</p>
                  </div>
                </div>
                <div class="flow-item">
                  <span class="flow-index">03</span>
                  <div>
                    <strong>DeepSeek 辅助建议</strong>
                    <p>生成面向患者可理解的个性化管理建议</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="cta">
            <el-button type="primary" size="large" class="cta-btn" @click="startQuestionnaire">
              <i class="iconfont-sys">&#xe621;</i>
              立即开始评估
            </el-button>
          </div>

          <ul class="trust">
            <li><i class="dot-sm"></i> XGBoost 机器学习模型</li>
            <li><i class="dot-sm"></i> SHAP 可解释性分析</li>
            <li><i class="dot-sm"></i> 自动保存草稿</li>
            <li><i class="dot-sm"></i> 数据加密存储</li>
            <li><i class="dot-sm"></i> DeepSeek AI 智能建议</li>
          </ul>
        </div>
        <div class="decor decor-1"></div>
        <div class="decor decor-2"></div>
        <div class="decor decor-3"></div>
      </div>
    </Transition>

    <!-- 问卷内容区域 - 带过渡动画 -->
    <Transition name="form-slide">
      <div v-show="showQuestionnaire" class="questionnaire-content-wrap">
        <!-- 步骤条 -->
        <ElSteps
          :active="currentStep"
          align-center
          finish-status="success"
          class="questionnaire-steps"
        >
          <ElStep title="基本信息" description="年龄/性别/身高体重" />
          <ElStep title="生活习惯" description="吸烟/饮酒/运动饮食" />
          <ElStep title="疾病史" description="慢性病/家族史" />
          <ElStep title="症状自查" description="近期症状" />
        </ElSteps>

        <!-- 问卷内容 -->
        <ElCard ref="formCardRef" class="questionnaire-content" shadow="hover">
          <ElForm ref="formRef" :model="questionnaireData" label-position="top">
            <!-- 第1步：基本信息 -->
            <BasicInfo
              v-show="currentStep === 0"
              ref="basicInfoRef"
              v-model:form-data="questionnaireData.basicInfo"
            />

            <!-- 第2步：生活习惯 -->
            <Lifestyle
              v-show="currentStep === 1"
              ref="lifestyleRef"
              v-model:form-data="questionnaireData.lifestyle"
            />

            <!-- 第3步：疾病史 -->
            <MedicalHistory
              v-show="currentStep === 2"
              ref="medicalHistoryRef"
              v-model:form-data="questionnaireData.medicalHistory"
            />

            <!-- 第4步：症状自查 -->
            <Symptoms
              v-show="currentStep === 3"
              ref="symptomsRef"
              v-model:form-data="questionnaireData.symptoms"
            />
          </ElForm>
        </ElCard>

        <!-- 操作按钮 -->
        <div class="questionnaire-actions">
          <ElButton v-if="currentStep > 0" size="large" @click="prevStep">
            <i class="iconfont-sys">&#xe625;</i>
            上一步
          </ElButton>
          <ElButton v-if="currentStep < 3" type="primary" size="large" @click="nextStep">
            下一步
            <i class="iconfont-sys">&#xe624;</i>
          </ElButton>
          <ElButton
            v-if="currentStep === 3"
            type="primary"
            size="large"
            :loading="submitLoading"
            @click="submitQuestionnaire"
          >
            <i class="iconfont-sys">&#xe621;</i>
            提交评估
          </ElButton>
        </div>

        <!-- 草稿提示 -->
        <div v-if="hasDraft" class="draft-tips">
          <ElAlert type="success" :closable="false" show-icon>
            <template #title>已自动保存草稿，您可以随时继续填写</template>
          </ElAlert>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import type { FormInstance } from 'element-plus'
  import BasicInfo from './steps/BasicInfo.vue'
  import Lifestyle from './steps/Lifestyle.vue'
  import MedicalHistory from './steps/MedicalHistory.vue'
  import Symptoms from './steps/Symptoms.vue'
  import { submitAssessmentV2, type QuestionnaireV2Request } from '@/api/assessment-v2'

  const router = useRouter()

  // 表单实例
  const formRef = ref<FormInstance>()
  const formCardRef = ref()
  const basicInfoRef = ref()
  const lifestyleRef = ref()
  const medicalHistoryRef = ref()
  const symptomsRef = ref()

  // 当前步骤
  const currentStep = ref(0)
  const submitLoading = ref(false)
  const hasDraft = ref(false)

  // 控制显示问卷还是 Hero
  const showQuestionnaire = ref(false)

  // 问卷数据
  const questionnaireData = reactive({
    basicInfo: {
      name: '',
      age: null as number | null,
      gender: '男',
      ethnicity: '汉族',
      height: null as number | null,
      weight: null as number | null,
      occupation: ''
    },
    lifestyle: {
      smokingStatus: '从不吸烟',
      quitSmokingYears: null as number | null,
      smokingAmount: null as number | null,
      smokingYears: null as number | null,
      alcoholStatus: '从不饮酒',
      alcoholFrequency: null as number | null,
      alcoholType: [] as string[],
      exerciseFrequency: '几乎不运动',
      dietHabits: [] as string[],
      sleepHours: 7 as number | null,
      sleepQuality: '良好',
      // 详细饮食习惯
      vegetableFruitIntake: '每天',
      redMeatIntake: '每周2-3次',
      processedFoodIntake: '偶尔',
      pickledFoodIntake: '很少',
      dairyIntake: '每天',
      // 精神压力与作息
      stressLevel: '中',
      workRestPattern: '规律',
      mentalHealth: '良好'
    },
    medicalHistory: {
      chronicDiseases: [] as string[],
      hepatitisType: [] as string[],
      familyCancerHistory: [] as string[],
      familyRelation: [] as string[],
      hasSurgery: false,
      surgeryName: '',
      surgeryDate: '',
      longTermMedication: [] as string[],
      otherMedication: '',
      // 环境与职业暴露
      hasOccupationalExposure: false,
      occupationalExposureTypes: [] as string[],
      airQuality: '良好',
      hasPollutionExposure: false,
      livingEnvironment: '城市',
      // 女性特有因素
      gender: '男', // 从basicInfo同步
      menstrualStatus: '正常',
      pregnancyCount: null as number | null,
      firstPregnancyAge: null as number | null,
      hasBreastfed: false,
      breastfeedingMonths: null as number | null,
      hormoneTherapyTypes: [] as string[],
      hormoneTherapyYears: null as number | null
    },
    symptoms: {
      recentSymptoms: [] as string[],
      abnormalFindings: [] as string[],
      otherAbnormalities: '',
      lastCheckup: '1年内',
      // 筛查历史
      screeningItems: [] as string[],
      tumorMarkersResult: '正常',
      abnormalMarkers: '',
      hasAbnormalHistory: false,
      abnormalResultsCount: null as number | null,
      abnormalResultsDetail: '',
      additionalNotes: ''
    }
  })

  // 开始问卷
  const startQuestionnaire = () => {
    showQuestionnaire.value = true
    nextTick(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })
  }

  // 滚动到表单顶部
  const scrollToFormTop = () => {
    // 延迟一点点，确保 DOM 已更新
    setTimeout(() => {
      // 查找所有可能的滚动容器（包括可以滚动的元素）
      const findScrollableParent = (element: HTMLElement | null): HTMLElement | null => {
        if (!element) return null

        const hasScrollableContent = (el: HTMLElement) => {
          const style = window.getComputedStyle(el)
          const isScrollable =
            style.overflow === 'auto' ||
            style.overflow === 'scroll' ||
            style.overflowY === 'auto' ||
            style.overflowY === 'scroll'
          return isScrollable && el.scrollHeight > el.clientHeight
        }

        let current = element.parentElement
        while (current) {
          if (hasScrollableContent(current)) {
            return current
          }
          current = current.parentElement
        }
        return null
      }
      // 从表单卡片开始查找可滚动的父元素
      const formCard = document.querySelector('.questionnaire-content')
      const scrollContainer = findScrollableParent(formCard as HTMLElement)
      if (scrollContainer) {
        scrollContainer.scrollTo({
          top: 0,
          behavior: 'smooth'
        })
      } else {
        // 如果没找到特定容器，尝试滚动 window 和主要元素
        window.scrollTo({ top: 0, behavior: 'smooth' })
        document.documentElement.scrollTo({ top: 0, behavior: 'smooth' })

        // 尝试滚动 el-main（Element Plus 布局的主内容区）
        const elMain = document.querySelector('.el-main')
        if (elMain) {
          elMain.scrollTo({ top: 0, behavior: 'smooth' })
        }
      }
    }, 100)
  }

  // 下一步
  const nextStep = async () => {
    // 保存草稿
    saveDraft()

    if (currentStep.value < 3) {
      currentStep.value++
      // 滚动到表单顶部
      scrollToFormTop()
    }
  }

  // 上一步
  const prevStep = () => {
    if (currentStep.value > 0) {
      currentStep.value--
      // 滚动到表单顶部
      scrollToFormTop()
    }
  }

  // 保存草稿
  const saveDraft = () => {
    const draftData = {
      ...questionnaireData,
      currentStep: currentStep.value,
      savedAt: new Date().toISOString()
    }
    localStorage.setItem('questionnaire_draft', JSON.stringify(draftData))
    hasDraft.value = true
  }

  // 恢复草稿
  const restoreDraft = () => {
    const draft = localStorage.getItem('questionnaire_draft')
    if (draft) {
      try {
        const draftData = JSON.parse(draft)

        ElMessageBox.confirm('检测到未完成的问卷，是否继续填写？', '提示', {
          confirmButtonText: '继续填写',
          cancelButtonText: '重新开始',
          type: 'info'
        })
          .then(() => {
            // 恢复数据
            Object.assign(questionnaireData.basicInfo, draftData.basicInfo)
            Object.assign(questionnaireData.lifestyle, draftData.lifestyle)
            Object.assign(questionnaireData.medicalHistory, draftData.medicalHistory)
            Object.assign(questionnaireData.symptoms, draftData.symptoms)
            currentStep.value = draftData.currentStep || 0
            hasDraft.value = true
            ElMessage.success('已恢复草稿数据')
          })
          .catch(() => {
            // 清除草稿
            localStorage.removeItem('questionnaire_draft')
            ElMessage.info('已清除草稿，开始新的填写')
          })
      } catch (e) {
        console.error('恢复草稿失败', e)
        localStorage.removeItem('questionnaire_draft')
      }
    }
  }

  // 提交问卷
  const submitQuestionnaire = async () => {
    submitLoading.value = true

    try {
      // 转换问卷数据为 V2 API 格式
      const submitData: QuestionnaireV2Request = {
        // 基础信息
        age: questionnaireData.basicInfo.age || 50,
        gender: questionnaireData.basicInfo.gender as '男' | '女',
        height: questionnaireData.basicInfo.height || 165,
        weight: questionnaireData.basicInfo.weight || 60,

        // 生活习惯
        smoking_status:
          questionnaireData.lifestyle.smokingStatus === '从不吸烟'
            ? 0
            : questionnaireData.lifestyle.smokingStatus === '已戒烟'
              ? 1
              : 2,
        smoking_years: questionnaireData.lifestyle.smokingYears || undefined,
        smoking_amount: questionnaireData.lifestyle.smokingAmount || undefined,
        alcohol_frequency: questionnaireData.lifestyle.alcoholStatus,
        alcohol_amount: questionnaireData.lifestyle.alcoholFrequency || undefined,
        exercise_hours_per_week:
          questionnaireData.lifestyle.exerciseFrequency === '几乎不运动'
            ? 0
            : questionnaireData.lifestyle.exerciseFrequency === '偶尔运动'
              ? 1
              : questionnaireData.lifestyle.exerciseFrequency === '每周1-2次'
                ? 1.5
                : 3.5,
        exercise_intensity: '中',
        sleep_hours: questionnaireData.lifestyle.sleepHours || 7,
        sleep_quality: questionnaireData.lifestyle.sleepQuality,

        // 详细饮食习惯
        vegetable_fruit_intake: questionnaireData.lifestyle.vegetableFruitIntake,
        red_meat_intake: questionnaireData.lifestyle.redMeatIntake,
        processed_food_intake: questionnaireData.lifestyle.processedFoodIntake,
        pickled_food_intake: questionnaireData.lifestyle.pickledFoodIntake,
        dairy_intake: questionnaireData.lifestyle.dairyIntake,

        // 疾病史
        chronic_diseases: questionnaireData.medicalHistory.chronicDiseases.filter(
          (d) => d !== '无'
        ),
        family_cancer_history: {
          has_history:
            questionnaireData.medicalHistory.familyCancerHistory.length > 0 &&
            !questionnaireData.medicalHistory.familyCancerHistory.includes('无家族肿瘤史'),
          relation: questionnaireData.medicalHistory.familyRelation.join('、'),
          cancer_types: questionnaireData.medicalHistory.familyCancerHistory.filter(
            (c) => c !== '无家族肿瘤史'
          )
        },
        personal_cancer_history: 0,
        surgery_history: questionnaireData.medicalHistory.hasSurgery
          ? [questionnaireData.medicalHistory.surgeryName]
          : [],
        medication_history: questionnaireData.medicalHistory.longTermMedication.filter(
          (m) => m !== '无'
        ),

        // 环境与职业暴露
        occupational_exposure: {
          has_exposure: questionnaireData.medicalHistory.hasOccupationalExposure,
          types: questionnaireData.medicalHistory.occupationalExposureTypes
        },
        environmental_factors: {
          air_quality: questionnaireData.medicalHistory.airQuality,
          pollution_exposure: questionnaireData.medicalHistory.hasPollutionExposure
        },
        living_environment: questionnaireData.medicalHistory.livingEnvironment,

        // 女性特有因素（仅女性）
        menstrual_status:
          questionnaireData.basicInfo.gender === '女'
            ? questionnaireData.medicalHistory.menstrualStatus
            : undefined,
        pregnancy_history:
          questionnaireData.basicInfo.gender === '女' &&
          questionnaireData.medicalHistory.pregnancyCount
            ? {
                pregnancy_count: questionnaireData.medicalHistory.pregnancyCount,
                first_pregnancy_age: questionnaireData.medicalHistory.firstPregnancyAge || undefined
              }
            : undefined,
        breastfeeding_history:
          questionnaireData.basicInfo.gender === '女' &&
          questionnaireData.medicalHistory.hasBreastfed
            ? {
                has_breastfed: true,
                total_months: questionnaireData.medicalHistory.breastfeedingMonths || undefined
              }
            : undefined,
        hormone_therapy:
          questionnaireData.basicInfo.gender === '女' &&
          questionnaireData.medicalHistory.hormoneTherapyTypes.length > 0 &&
          !questionnaireData.medicalHistory.hormoneTherapyTypes.includes('none')
            ? {
                contraceptive_use:
                  questionnaireData.medicalHistory.hormoneTherapyTypes.includes('contraceptive'),
                hrt_use: questionnaireData.medicalHistory.hormoneTherapyTypes.includes('hrt'),
                duration_years: questionnaireData.medicalHistory.hormoneTherapyYears || undefined
              }
            : undefined,

        // 精神压力与作息
        stress_level: questionnaireData.lifestyle.stressLevel,
        work_rest_pattern: questionnaireData.lifestyle.workRestPattern,
        mental_health: questionnaireData.lifestyle.mentalHealth,

        // 体检与筛查历史
        screening_history: {
          last_checkup: questionnaireData.symptoms.lastCheckup,
          tumor_markers: questionnaireData.symptoms.screeningItems.includes('tumor_markers'),
          imaging:
            questionnaireData.symptoms.screeningItems.includes('chest_ct') ||
            questionnaireData.symptoms.screeningItems.includes('abdominal_ultrasound'),
          endoscopy:
            questionnaireData.symptoms.screeningItems.includes('gastroscopy') ||
            questionnaireData.symptoms.screeningItems.includes('colonoscopy')
        },
        abnormal_results_history:
          questionnaireData.symptoms.hasAbnormalHistory &&
          questionnaireData.symptoms.abnormalResultsDetail
            ? [
                {
                  type: '综合异常',
                  date: new Date().toISOString().split('T')[0],
                  description: questionnaireData.symptoms.abnormalResultsDetail
                }
              ]
            : [],
        last_checkup: questionnaireData.symptoms.lastCheckup,

        // 症状自查
        symptoms: questionnaireData.symptoms.recentSymptoms.filter((s) => s !== '无明显症状'),
        recent_abnormalities: questionnaireData.symptoms.abnormalFindings.filter(
          (a) => a !== '无异常'
        ),

        // 备注
        notes: questionnaireData.symptoms.additionalNotes || undefined
      }

      console.log('提交问卷数据：', submitData)

      // 调用评估 API
      const result = await submitAssessmentV2(submitData)

      console.log('评估结果（原始）：', result)

      // request 工具已经自动解包了 response.data.data
      // 所以 result 就是后端返回的 data 字段内容
      if (!result) {
        throw new Error('后端返回数据为空，请检查后端接口')
      }

      if (!result.assessment_id) {
        console.error('后端返回格式异常:', result)
        throw new Error('后端返回数据格式错误，缺少 assessment_id')
      }

      console.log('评估ID:', result.assessment_id)

      // 清除草稿
      localStorage.removeItem('questionnaire_draft')

      ElMessage.success('问卷提交成功！正在生成风险评估报告...')

      // 跳转到评估结果页面，所有数据都通过 state 传递（不使用 params）
      router.push({
        name: 'ReportDetail',
        params: {
          id: result.assessment_id // 仍需保留 id 参数（路由定义要求）
        },
        state: {
          reportData: result as any,
          assessmentId: result.assessment_id // 同时在 state 中传递 ID
        }
      })
    } catch (error: any) {
      console.error('提交失败:', error)
      ElMessage.error(error?.message || '提交失败，请重试')
    } finally {
      submitLoading.value = false
    }
  }

  // 自动保存
  let autoSaveTimer: ReturnType<typeof setInterval> | null = null
  const startAutoSave = () => {
    // 每30秒自动保存一次
    autoSaveTimer = setInterval(() => {
      saveDraft()
    }, 30000)
  }

  // 组件挂载时恢复草稿
  onMounted(() => {
    restoreDraft()
    startAutoSave()
  })

  // 组件卸载时清除定时器
  onBeforeUnmount(() => {
    if (autoSaveTimer) {
      clearInterval(autoSaveTimer)
    }
  })

  // 同步性别信息到medicalHistory（用于女性特有字段显示）
  watch(
    () => questionnaireData.basicInfo.gender,
    (newGender) => {
      questionnaireData.medicalHistory.gender = newGender
    },
    { immediate: true }
  )

  // 监听数据变化自动保存
  watch(
    () => questionnaireData,
    () => {
      if (hasDraft.value) {
        saveDraft()
      }
    },
    { deep: true }
  )
</script>

<style scoped lang="scss">
  .questionnaire-container {
    position: relative;
    min-height: calc(100vh - 120px);
    overflow: hidden;
    background:
      radial-gradient(
        1200px 600px at 20% 0%,
        color-mix(in srgb, var(--el-color-primary) 12%, #fff) 0%,
        transparent 60%
      ),
      linear-gradient(180deg, #fff, #fff);
  }

  .questionnaire-container::before {
    position: absolute;
    inset: 0;
    pointer-events: none;
    content: '';
    background-image:
      linear-gradient(to right, rgb(0 0 0 / 3%) 1px, transparent 1px),
      linear-gradient(to bottom, rgb(0 0 0 / 3%) 1px, transparent 1px);
    background-size: 32px 32px;
  }

  /* ============================================
   Hero 区域过渡动画：淡出 + 向上滑动消失
   ============================================ */
  .hero-fade-enter-active {
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .hero-fade-leave-active {
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .hero-fade-enter-from {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }

  .hero-fade-leave-to {
    opacity: 0;
    transform: translateY(-60px) scale(0.95);
  }

  .hero-fade-enter-to,
  .hero-fade-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  /* ============================================
   表单区域过渡动画：淡入 + 从下方滑入
   ============================================ */
  .form-slide-enter-active {
    transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
    transition-delay: 0.2s; /* 延迟0.2s，等Hero消失后再出现 */
  }

  .form-slide-leave-active {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .form-slide-enter-from {
    opacity: 0;
    transform: translateY(50px) scale(0.96);
  }

  .form-slide-leave-to {
    opacity: 0;
    transform: translateY(-30px) scale(0.98);
  }

  .form-slide-enter-to,
  .form-slide-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  /* Hero 区域样式 */
  .questionnaire-hero {
    position: relative;
    padding: 120px 32px 96px;
  }

  .hero-inner {
    position: relative;
    z-index: 1;
    max-width: 920px;
    margin: 0 auto;
    text-align: center;
  }

  .badge-row {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    padding: 6px 12px;
    font-size: 13px;
    color: var(--el-color-primary);
    background: rgb(64 158 255 / 8%);
    border-radius: 999px;
  }

  .badge-row .dot {
    width: 8px;
    height: 8px;
    background: var(--el-color-primary);
    border-radius: 50%;
  }

  .badge-row .sep {
    color: rgb(0 0 0 / 35%);
  }

  .title-main {
    margin: 24px 0 0;
    font-size: 72px;
    font-weight: 800;
    line-height: 1.05;
    color: color-mix(in srgb, var(--el-color-primary) 78%, #92a7bd);
    letter-spacing: 1px;
  }

  .title-sub {
    margin: 10px 0 0;
    font-size: 60px;
    font-weight: 900;
    line-height: 1.05;
    color: #1f2330;
  }

  .desc {
    max-width: 780px;
    margin: 22px auto 0;
    font-size: 18px;
    line-height: 1.6;
    color: var(--art-text-gray-700, #4b5563);
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    justify-content: center;
    margin-top: 24px;
  }

  .chip {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    padding: 10px 14px;
    font-size: 15px;
    color: #374151;
    background: #fff;
    border-radius: 999px;
    box-shadow: 0 6px 18px rgb(0 0 0 / 6%);
  }

  .hero-showcase {
    display: grid;
    grid-template-columns: 1.2fr 0.9fr;
    gap: 22px;
    max-width: 1040px;
    margin: 34px auto 0;
    text-align: left;
  }

  .showcase-panel {
    position: relative;
    padding: 24px 24px 22px;
    background:
      linear-gradient(145deg, rgb(255 255 255 / 90%), rgb(255 255 255 / 72%)),
      linear-gradient(135deg, #d8ecff, #fff1dc);
    backdrop-filter: blur(16px);
    border: 1px solid rgb(255 255 255 / 70%);
    border-radius: 24px;
    box-shadow:
      0 18px 60px rgb(33 62 92 / 10%),
      inset 0 1px 0 rgb(255 255 255 / 90%);
  }

  .panel-eyebrow {
    display: inline-flex;
    padding: 6px 10px;
    margin-bottom: 14px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #0f6cbd;
    background: rgb(15 108 189 / 10%);
    border-radius: 999px;
  }

  .mission-panel h3,
  .architecture-panel h3 {
    margin: 0 0 10px;
    font-size: 24px;
    line-height: 1.3;
    color: #172033;
  }

  .mission-panel p {
    margin: 0;
    font-size: 15px;
    line-height: 1.7;
    color: #556072;
  }

  .mission-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 18px;
  }

  .mission-item {
    padding: 16px 14px;
    background: rgb(255 255 255 / 62%);
    border: 1px solid rgb(15 108 189 / 10%);
    border-radius: 18px;
  }

  .mission-value {
    display: block;
    margin-bottom: 6px;
    font-size: 22px;
    font-weight: 800;
    color: #102a56;
  }

  .mission-label {
    font-size: 13px;
    line-height: 1.5;
    color: #5d697d;
  }

  .flow-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .flow-item {
    display: grid;
    grid-template-columns: 52px 1fr;
    gap: 14px;
    align-items: start;
    padding: 12px 0;
    border-bottom: 1px dashed rgb(16 42 86 / 12%);
  }

  .flow-item:last-child {
    padding-bottom: 0;
    border-bottom: none;
  }

  .flow-index {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    font-size: 14px;
    font-weight: 800;
    color: #fff;
    background: linear-gradient(135deg, #0f6cbd, #25a6f7);
    border-radius: 16px;
    box-shadow: 0 12px 24px rgb(37 166 247 / 22%);
  }

  .flow-item strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
    color: #15233e;
  }

  .flow-item p {
    margin: 0;
    font-size: 13px;
    line-height: 1.6;
    color: #617086;
  }

  .cta {
    display: flex;
    gap: 14px;
    justify-content: center;
    margin-top: 32px;
  }

  .cta-btn {
    padding: 16px 32px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 14px;

    .iconfont-sys {
      margin-right: 6px;
      font-size: 18px;
    }
  }

  .trust {
    display: flex;
    flex-wrap: wrap;
    gap: 26px;
    justify-content: center;
    margin-top: 30px;
    margin-bottom: 24px;
    font-size: 15px;
    color: #6b7280;
  }

  .trust .dot-sm {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin-right: 6px;
    background: var(--el-color-success, #22c55e);
    border-radius: 50%;
  }

  .decor {
    position: absolute;
    filter: blur(12px);
    border-radius: 16px;
    opacity: 0.25;
  }

  .decor-1 {
    top: 120px;
    left: -40px;
    width: 220px;
    height: 220px;
    background: var(--el-color-primary);
  }

  .decor-2 {
    top: -40px;
    right: -60px;
    width: 320px;
    height: 320px;
    background: #a78bfa;
  }

  .decor-3 {
    right: 120px;
    bottom: 60px;
    width: 180px;
    height: 180px;
    background: #60a5fa;
  }

  /* 问卷内容区域样式 */
  .questionnaire-content-wrap {
    max-width: 1200px;
    padding: 20px;
    margin: 0 auto;

    .questionnaire-steps {
      padding: 20px;
      margin-bottom: 30px;
      background: rgb(255 255 255 / 80%);
      backdrop-filter: blur(10px);
      border-radius: 8px;
    }

    .questionnaire-content {
      min-height: 500px;
      margin-bottom: 20px;

      :deep(.el-card__body) {
        padding: 40px;
      }
    }

    .questionnaire-actions {
      display: flex;
      gap: 20px;
      justify-content: center;
      padding: 20px 0;

      .el-button {
        min-width: 120px;

        .iconfont-sys {
          margin: 0 4px;
          font-size: 14px;
        }
      }
    }

    .draft-tips {
      max-width: 600px;
      margin-top: 20px;
      margin-right: auto;
      margin-left: auto;
    }
  }

  // 响应式适配
  @media (width <= 768px) {
    .title-main {
      font-size: 40px;
    }

    .title-sub {
      font-size: 36px;
    }

    .desc {
      font-size: 15px;
    }

    .questionnaire-hero {
      padding: 84px 16px 48px;
    }

    .hero-showcase {
      grid-template-columns: 1fr;
    }

    .mission-grid {
      grid-template-columns: 1fr;
    }

    .questionnaire-content-wrap {
      padding: 10px;

      .questionnaire-content {
        :deep(.el-card__body) {
          padding: 20px;
        }
      }

      .questionnaire-actions {
        flex-direction: column;

        .el-button {
          width: 100%;
        }
      }
    }
  }
</style>
