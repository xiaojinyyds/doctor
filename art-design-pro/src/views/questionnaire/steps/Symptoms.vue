<template>
  <div class="step-container">
    <h3 class="step-title">
      <i class="iconfont-sys">&#xe7ad;</i>
      症状自查与筛查历史
    </h3>
    <p class="step-desc">请告知您近期症状和体检筛查情况</p>

    <ElForm :model="formData" :rules="rules" label-width="160px" class="step-form">
      <!-- 近期症状 -->
      <ElFormItem label="近期症状">
        <ElCheckboxGroup v-model="formData.recentSymptoms">
          <div class="symptom-grid">
            <ElCheckbox label="持续咳嗽">持续咳嗽</ElCheckbox>
            <ElCheckbox label="咳血">咳血</ElCheckbox>
            <ElCheckbox label="胸痛/胸闷">胸痛/胸闷</ElCheckbox>
            <ElCheckbox label="呼吸困难">呼吸困难</ElCheckbox>
            <ElCheckbox label="不明原因体重下降">不明原因体重下降</ElCheckbox>
            <ElCheckbox label="持续发热">持续发热</ElCheckbox>
            <ElCheckbox label="腹痛/腹胀">腹痛/腹胀</ElCheckbox>
            <ElCheckbox label="便血/黑便">便血/黑便</ElCheckbox>
            <ElCheckbox label="吞咽困难">吞咽困难</ElCheckbox>
            <ElCheckbox label="持续消化不良">持续消化不良</ElCheckbox>
            <ElCheckbox label="乳房肿块">乳房肿块</ElCheckbox>
            <ElCheckbox label="无明显症状">无明显症状</ElCheckbox>
          </div>
        </ElCheckboxGroup>
      </ElFormItem>

      <ElDivider />

      <!-- 异常发现 -->
      <ElFormItem label="近期检查异常发现">
        <ElCheckboxGroup v-model="formData.abnormalFindings">
          <div class="abnormal-grid">
            <ElCheckbox label="肺部结节">肺部结节</ElCheckbox>
            <ElCheckbox label="肝脏囊肿">肝脏囊肿</ElCheckbox>
            <ElCheckbox label="胃肠息肉">胃肠息肉</ElCheckbox>
            <ElCheckbox label="甲状腺结节">甲状腺结节</ElCheckbox>
            <ElCheckbox label="乳腺增生">乳腺增生</ElCheckbox>
            <ElCheckbox label="前列腺增生">前列腺增生</ElCheckbox>
            <ElCheckbox label="无异常">无异常</ElCheckbox>
          </div>
        </ElCheckboxGroup>
      </ElFormItem>

      <ElRow v-if="formData.abnormalFindings.some(item => !['无异常'].includes(item))" :gutter="20">
        <ElCol :span="24">
          <ElFormItem label="其他异常">
            <ElInput
              v-model="formData.otherAbnormalities"
              placeholder="如有其他检查异常，请详细描述"
              type="textarea"
              :rows="3"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider content-position="left">
        <span style="color: var(--el-color-primary); font-weight: 600;">🏥 体检与筛查历史（V2.0新增）</span>
      </ElDivider>

      <!-- 上次体检时间 -->
      <ElFormItem label="上次全面体检时间" prop="lastCheckup">
        <ElRadioGroup v-model="formData.lastCheckup">
          <ElRadio label="半年内">半年内</ElRadio>
          <ElRadio label="1年内">1年内</ElRadio>
          <ElRadio label="1-3年">1-3年</ElRadio>
          <ElRadio label="3年以上">3年以上</ElRadio>
          <ElRadio label="从未">从未体检</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 筛查项目 -->
      <ElFormItem label="近期完成的筛查项目">
        <ElCheckboxGroup v-model="formData.screeningItems">
          <div class="screening-grid">
            <ElCheckbox label="tumor_markers">肿瘤标志物检查</ElCheckbox>
            <ElCheckbox label="chest_ct">胸部CT</ElCheckbox>
            <ElCheckbox label="abdominal_ultrasound">腹部超声</ElCheckbox>
            <ElCheckbox label="gastroscopy">胃镜</ElCheckbox>
            <ElCheckbox label="colonoscopy">肠镜</ElCheckbox>
            <ElCheckbox label="mammography">乳腺钼靶/超声</ElCheckbox>
            <ElCheckbox label="none">未做筛查</ElCheckbox>
          </div>
        </ElCheckboxGroup>
        <div class="field-tip">
          <i class="el-icon-info"></i>
          请勾选近1年内完成的肿瘤筛查项目
        </div>
      </ElFormItem>

      <!-- 肿瘤标志物详情 -->
      <template v-if="formData.screeningItems.includes('tumor_markers')">
        <ElFormItem label="肿瘤标志物结果">
          <ElRadioGroup v-model="formData.tumorMarkersResult">
            <ElRadio label="正常">正常</ElRadio>
            <ElRadio label="轻度升高">轻度升高</ElRadio>
            <ElRadio label="中度升高">中度升高</ElRadio>
            <ElRadio label="显著升高">显著升高</ElRadio>
          </ElRadioGroup>
        </ElFormItem>

        <ElRow v-if="formData.tumorMarkersResult !== '正常'" :gutter="20">
          <ElCol :span="24">
            <ElFormItem label="异常指标">
              <ElInput
                v-model="formData.abnormalMarkers"
                placeholder="例如：CEA 8.5 ng/ml, CA19-9 45 U/ml"
                type="textarea"
                :rows="2"
              />
            </ElFormItem>
          </ElCol>
        </ElRow>
      </template>

      <!-- 异常结果历史 -->
      <ElFormItem label="是否有历史异常结果" prop="hasAbnormalHistory">
        <ElRadioGroup v-model="formData.hasAbnormalHistory">
          <ElRadio :label="false">无</ElRadio>
          <ElRadio :label="true">有</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <template v-if="formData.hasAbnormalHistory">
        <ElFormItem label="异常结果数量" prop="abnormalResultsCount">
          <ElInputNumber
            v-model="formData.abnormalResultsCount"
            :min="0"
            :max="50"
            placeholder="请输入异常结果数量"
            style="width: 100%"
          >
            <template #append>项</template>
          </ElInputNumber>
        </ElFormItem>

        <ElRow :gutter="20">
          <ElCol :span="24">
            <ElFormItem label="异常结果详情">
              <ElInput
                v-model="formData.abnormalResultsDetail"
                placeholder="请描述异常结果的类型和时间，例如：2023年肺部CT发现小结节（6mm）"
                type="textarea"
                :rows="4"
              />
              <div class="field-tip">
                <i class="el-icon-info"></i>
                请详细描述异常结果的具体内容、发现时间及后续处理情况
              </div>
            </ElFormItem>
          </ElCol>
        </ElRow>
      </template>

      <ElDivider />

      <!-- 补充说明 -->
      <ElFormItem label="其他补充说明">
        <ElInput
          v-model="formData.additionalNotes"
          placeholder="如有其他需要说明的健康情况，请在此填写"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
        />
      </ElFormItem>
    </ElForm>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import type { FormRules } from 'element-plus'

interface FormData {
  recentSymptoms: string[]
  abnormalFindings: string[]
  otherAbnormalities: string
  lastCheckup: string
  screeningItems: string[]
  tumorMarkersResult: string
  abnormalMarkers: string
  hasAbnormalHistory: boolean
  abnormalResultsCount: number | null
  abnormalResultsDetail: string
  additionalNotes: string
}

const formData = defineModel<FormData>('formData', { required: true })

// 表单验证规则
const rules: FormRules = {
  lastCheckup: [{ required: true, message: '请选择上次体检时间', trigger: 'change' }],
  hasAbnormalHistory: [{ required: true, message: '请选择是否有历史异常结果', trigger: 'change' }]
}

// 监听"无"选项，自动取消其他选项
watch(
  () => formData.value.recentSymptoms,
  (newVal) => {
    if (newVal.includes('无明显症状') && newVal.length > 1) {
      formData.value.recentSymptoms = ['无明显症状']
    }
  }
)

watch(
  () => formData.value.abnormalFindings,
  (newVal) => {
    if (newVal.includes('无异常') && newVal.length > 1) {
      formData.value.abnormalFindings = ['无异常']
    }
  }
)

watch(
  () => formData.value.screeningItems,
  (newVal) => {
    if (newVal.includes('none') && newVal.length > 1) {
      formData.value.screeningItems = ['none']
    }
  }
)

defineExpose({ rules })
</script>

<style scoped lang="scss">
.step-container {
  .step-title {
    font-size: 20px;
    color: var(--art-text-gray-800);
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;

    .iconfont-sys {
      color: var(--el-color-primary);
      font-size: 24px;
    }
  }

  .step-desc {
    color: var(--art-text-gray-500);
    margin: 0 0 30px 0;
    font-size: 14px;
  }

  .step-form {
    :deep(.el-checkbox),
    :deep(.el-radio) {
      margin-right: 20px;
      margin-bottom: 12px;
    }

    :deep(.el-input-number) {
      width: 100%;
    }

    .symptom-grid,
    .abnormal-grid,
    .screening-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 10px;

      @media (max-width: 768px) {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    .field-tip {
      margin-top: 8px;
      padding: 8px 12px;
      background: var(--el-color-info-light-9);
      border-left: 3px solid var(--el-color-info);
      border-radius: 4px;
      font-size: 13px;
      color: var(--el-color-info);
      line-height: 1.5;

      i {
        margin-right: 6px;
      }
    }
  }
}
</style>
