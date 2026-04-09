<template>
  <div class="records-wrap">
    <div class="records-hero" :class="{ compact: showForm }">
      <div class="hero-inner">
        <div class="badge-row">
          <span class="dot"></span>
          <span class="badge">肿瘤风险评估</span>
          <span class="sep">|</span>
          <span class="sub">申请与记录中心</span>
        </div>

        <h1 class="title-main">填写评估申请</h1>
        <h2 class="title-sub">从未如此简单</h2>
        <p class="desc"
          >一页式信息采集与智能校验，快速提交肿瘤风险评估申请，并随时查看历史记录与状态</p
        >

        <div class="chips">
          <span class="chip">
            <i class="el-icon-pie-chart"></i>
            结构化表单
          </span>
          <span class="chip">
            <i class="el-icon-lightning"></i>
            10分钟完成
          </span>
          <span class="chip">
            <i class="el-icon-check"></i>
            高通过率
          </span>
        </div>

        <div class="cta">
          <el-button type="primary" size="large" class="cta-btn" @click="goApply"
            >立即开始生成</el-button
          >
          <el-button size="large" class="ghost-btn" @click="goList">查看评估记录</el-button>
        </div>

        <ul class="trust">
          <li><i class="dot-sm"></i> 数据脱敏与加密</li>
          <li><i class="dot-sm"></i> 结构化字段校验</li>
          <li><i class="dot-sm"></i> 智能提示与缺失项检查</li>
          <li><i class="dot-sm"></i> 支持导出与归档</li>
          <li><i class="dot-sm"></i> 结果辅助解释</li>
        </ul>
      </div>
      <div class="decor decor-1"></div>
      <div class="decor decor-2"></div>
      <div class="decor decor-3"></div>
    </div>
    <div v-show="showForm" ref="formSection" class="apply-form-wrap">
      <div class="apply-hero">
        <h4 class="apply-hero-title">立即生成您的 肿瘤风险 评估申请</h4>
        <p class="apply-hero-sub">只需简单几步，AI将为您智能生成完整的评估申请材料</p>
      </div>
      <section class="apply-section">
        <div class="apply-header">
          <h3>快速开始评估申请</h3>
          <span class="step">步骤 {{ step }}/3</span>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          :hide-required-asterisk="true"
          label-position="top"
          class="apply-form"
        >
          <!-- Step 1: 基础信息，一个大容器包起来 -->
          <div v-show="step === 1" class="step-wrap step-wrap--one">
            <el-row :gutter="16" class="step-row">
              <el-col :md="12" :sm="24">
                <el-form-item prop="name" class="field-compact">
                  <template #label>
                    <el-icon class="label-ic"><User /></el-icon>
                    姓名
                  </template>
                  <el-input v-model="form.name" placeholder="申请人姓名" />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="phone" class="field-compact">
                  <template #label>
                    <el-icon class="label-ic"><Phone /></el-icon>
                    联系电话
                  </template>
                  <el-input v-model="form.phone" placeholder="便于联系与结果通知" />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="age" class="field-compact">
                  <template #label>
                    <el-icon class="label-ic"><Timer /></el-icon>
                    年龄
                  </template>
                  <el-input-number
                    v-model="form.age"
                    :min="0"
                    :max="150"
                    :step="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="gender" class="field-compact">
                  <template #label>
                    <el-icon class="label-ic"><Male /></el-icon>
                    性别
                  </template>
                  <el-radio-group v-model="form.gender">
                    <el-radio label="男" />
                    <el-radio label="女" />
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="height" class="field-compact">
                  <template #label>
                    <el-icon class="label-ic"><ScaleToOriginal /></el-icon>
                    身高(cm)
                  </template>
                  <el-input-number
                    v-model="form.height"
                    :min="0"
                    :max="300"
                    :step="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="weight" class="field-compact">
                  <template #label> 体重(kg) </template>
                  <el-input-number
                    v-model="form.weight"
                    :min="0"
                    :max="500"
                    :step="0.1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- Step 2: 生活方式/病史（本步仅含：吸烟、既往肿瘤史、运动、慢性病、症状） -->
          <div v-show="step === 2" class="step-wrap step-wrap--two">
            <el-row :gutter="16" class="step-row">
              <el-col :md="12" :sm="24">
                <el-form-item prop="smoking" class="field-compact">
                  <template #label> 吸烟 </template>
                  <el-select v-model="form.smoking" style="width: 100%">
                    <el-option label="否" :value="0" />
                    <el-option label="是" :value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="physical_activity" class="field-compact">
                  <template #label> 运动(小时/周) </template>
                  <el-input-number
                    v-model="form.physical_activity"
                    :min="0"
                    :max="168"
                    :step="0.5"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="cancer_history" class="field-compact">
                  <template #label> 既往肿瘤史 </template>
                  <el-select v-model="form.cancer_history" style="width: 100%">
                    <el-option label="无" :value="0" />
                    <el-option label="有" :value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="chronic_diseases" class="field-compact">
                  <template #label> 慢性病 </template>
                  <el-select
                    v-model="form.chronic_diseases"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option v-for="opt in chronicOptions" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="symptoms" class="field-compact">
                  <template #label> 症状 </template>
                  <el-select
                    v-model="form.symptoms"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option v-for="opt in symptomOptions" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- Step 3: 其余信息（饮酒、家族史、遗传风险、备注） -->
          <div v-show="step === 3" class="step-wrap step-wrap--three">
            <el-row :gutter="16" class="step-row">
              <el-col :md="12" :sm="24">
                <el-form-item prop="alcohol_intake" class="field-compact">
                  <template #label> 饮酒(份/周) </template>
                  <el-input-number
                    v-model="form.alcohol_intake"
                    :min="0"
                    :max="100"
                    :step="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="family_history" class="field-compact">
                  <template #label> 家族史 </template>
                  <el-select
                    v-model="form.family_history"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option v-for="opt in familyOptions" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :md="12" :sm="24">
                <el-form-item prop="genetic_risk" class="field-compact">
                  <template #label> 遗传风险 </template>
                  <el-select v-model="form.genetic_risk" style="width: 100%">
                    <el-option label="无/未知" :value="0" />
                    <el-option label="有" :value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item prop="notes">
                  <template #label>
                    <el-icon class="label-ic"><EditPen /></el-icon>
                    备注
                  </template>
                  <el-input
                    v-model="form.notes"
                    type="textarea"
                    :rows="3"
                    placeholder="可填写症状、就诊史或其他补充说明"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div class="apply-actions">
            <el-button v-if="step > 1" size="large" @click="prevStep">上一步</el-button>
            <el-button v-else size="large" @click="resetForm">重置</el-button>
            <el-button v-if="step < 3" type="primary" size="large" @click="nextStep"
              >进入下一步</el-button
            >
            <el-button v-else type="primary" size="large" @click="submitFinal">提交</el-button>
          </div>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
  defineOptions({ name: 'RiskRecords' })
  import { ElMessage } from 'element-plus'
  import { User, Phone, Timer, Male, ScaleToOriginal, EditPen } from '@element-plus/icons-vue'
  const router = useRouter()
  const formSection = ref<HTMLElement | null>(null)
  const showForm = ref(false)
  const step = ref(1)
  const goApply = () => {
    showForm.value = true
    nextTick(() => formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
  }

  const chronicOptions = ['高血压', '糖尿病', '冠心病']
  const familyOptions = ['胃癌', '肺癌', '肝癌', '乳腺癌']
  const symptomOptions = ['咳嗽', '胸痛', '乏力', '体重下降']
  const goList = () => router.push('/risk/apply')

  // 基础信息表单模型
  const formRef = ref()
  const form = reactive({
    name: '',
    phone: '',
    age: undefined as number | undefined,
    gender: '男',
    height: undefined as number | undefined,
    weight: undefined as number | undefined,
    smoking: 0,
    alcohol_intake: 0,
    physical_activity: 0,
    cancer_history: 0,
    chronic_diseases: [] as string[],
    family_history: [] as string[],
    symptoms: [] as string[],
    genetic_risk: 0,
    notes: ''
  })
  const rules = {
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    phone: [
      { required: true, message: '请输入联系电话', trigger: 'blur' },
      { pattern: /^\d[\d-]{5,20}$/i, message: '电话格式不正确', trigger: 'blur' }
    ],
    age: [{ required: true, message: '请输入年龄', trigger: 'change' }],
    gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
    height: [{ required: true, message: '请输入身高', trigger: 'change' }],
    weight: [{ required: true, message: '请输入体重', trigger: 'change' }]
  }

  function resetForm() {
    formRef.value?.resetFields?.()
    step.value = 1
  }
  const step1Fields = ['name', 'phone', 'age', 'gender', 'height', 'weight'] as unknown as string[]
  const step2Fields = [
    'smoking',
    'cancer_history',
    'physical_activity',
    'chronic_diseases',
    'symptoms'
  ] as unknown as string[]

  async function nextStep() {
    try {
      if (step.value === 1) {
        await (formRef.value?.validateField
          ? formRef.value.validateField(step1Fields)
          : formRef.value?.validate?.())
        step.value = 2
      } else if (step.value === 2) {
        if (formRef.value?.validateField) {
          await formRef.value.validateField(step2Fields)
        }
        step.value = 3
      }
      nextTick(() => formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
    } catch (err) {
      console.error('[RiskRecords] nextStep error:', err)
      ElMessage.error('请检查并补全必填信息')
    }
  }
  function prevStep() {
    step.value = Math.max(1, step.value - 1)
    nextTick(() => formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
  }
  async function submitFinal() {
    try {
      await formRef.value?.validate?.()
      ElMessage.success('提交成功')
    } catch (err) {
      ElMessage.error('提交失败')
      console.error('[RiskRecords] submitFinal error:', err)
    }
  }
</script>

<style scoped>
  .records-wrap {
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

  .records-wrap::before {
    position: absolute;
    inset: 0;
    pointer-events: none;
    content: '';
    background-image:
      linear-gradient(to right, rgb(0 0 0 / 3%) 1px, transparent 1px),
      linear-gradient(to bottom, rgb(0 0 0 / 3%) 1px, transparent 1px);
    background-size: 32px 32px;
  }

  .records-hero {
    position: relative;
    padding: 120px 32px 96px;
  }

  .records-hero.compact {
    padding-bottom: 24px; /* 展开表单时收紧底部空间，让下方表单更靠上 */
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

  .cta {
    display: flex;
    gap: 14px;
    justify-content: center;
    margin-top: 18px; /* 提高按钮位置 */
  }

  .cta-btn {
    padding: 16px 26px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 14px;
  }

  .ghost-btn {
    padding: 16px 26px;
    font-size: 16px;
    border-radius: 14px;
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

    .records-hero {
      padding: 84px 16px 48px;
    }
  }

  /* 表单区域 */
  .apply-form-wrap {
    max-width: 980px;
    padding: 0 16px;
    margin: 50px auto 36px; /* 与上方更紧密衔接 */
  }

  .apply-section {
    position: relative;
    padding: 18px 18px 12px;
    margin-bottom: 24px;
    background: transparent; /* 与上方背景融为一体 */
    border: 0 solid #ccc;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgb(0 0 0 / 8%);
  }

  .apply-hero {
    margin: 80px 0 60px;
    text-align: center;
  }

  .apply-hero-title {
    margin: 0;
    font-size: 34px;
    font-weight: 900;
    line-height: 1.2;
    color: transparent;
    letter-spacing: 0.5px;
    background: linear-gradient(90deg, var(--el-color-primary) 0%, #6b8bee 45%, #8b5cf6 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .apply-hero-sub {
    margin: 6px 0 0;
    font-size: 14px;
    color: #64748b;
  }

  .apply-section::before {
    position: absolute;
    top: 0;
    right: 18px;
    left: 18px;
    height: 1px;
    content: '';
    background: linear-gradient(90deg, transparent, rgb(0 0 0 / 8%), transparent);
  }

  .apply-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .apply-header h3 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
  }

  .apply-header .step {
    font-size: 13px;
    color: #909399;
  }

  .apply-form :deep(.el-form-item__label) {
    font-weight: 600;
    color: #000;
  }

  .label-ic {
    margin-top: 10px;
    margin-right: 6px;
    color: var(--el-color-primary);
  }

  .apply-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 8px;
  }
</style>
