<template>
  <div class="step-container">
    <h3 class="step-title">
      <i class="iconfont-sys">&#xe7b9;</i>
      疾病史与家族史
    </h3>
    <p class="step-desc">请告知您的既往病史和家族肿瘤史</p>

    <ElForm :model="formData" :rules="rules" label-width="140px" class="step-form">
      <!-- 慢性病史 -->
      <ElFormItem label="慢性病史">
        <ElCheckboxGroup v-model="formData.chronicDiseases">
          <ElCheckbox label="高血压">高血压</ElCheckbox>
          <ElCheckbox label="糖尿病">糖尿病</ElCheckbox>
          <ElCheckbox label="冠心病">冠心病</ElCheckbox>
          <ElCheckbox label="慢性肝炎">慢性肝炎</ElCheckbox>
          <ElCheckbox label="慢性胃炎/胃溃疡">慢性胃炎/胃溃疡</ElCheckbox>
          <ElCheckbox label="无">无</ElCheckbox>
        </ElCheckboxGroup>
      </ElFormItem>

      <ElRow v-if="formData.chronicDiseases.includes('慢性肝炎')" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="肝炎类型" prop="hepatitisType">
            <ElCheckboxGroup v-model="formData.hepatitisType">
              <ElCheckbox label="乙肝">乙肝</ElCheckbox>
              <ElCheckbox label="丙肝">丙肝</ElCheckbox>
              <ElCheckbox label="其他">其他</ElCheckbox>
            </ElCheckboxGroup>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider />

      <!-- 家族肿瘤史 -->
      <ElFormItem label="家族肿瘤史">
        <div class="family-history-wrapper">
          <ElAlert
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 15px"
          >
            <template #title>请勾选直系亲属（父母、兄弟姐妹）患过的肿瘤类型</template>
          </ElAlert>
          <ElCheckboxGroup v-model="formData.familyCancerHistory">
            <div class="cancer-type-grid">
              <ElCheckbox label="肺癌">肺癌</ElCheckbox>
              <ElCheckbox label="胃癌">胃癌</ElCheckbox>
              <ElCheckbox label="肝癌">肝癌</ElCheckbox>
              <ElCheckbox label="结直肠癌">结直肠癌</ElCheckbox>
              <ElCheckbox label="乳腺癌">乳腺癌</ElCheckbox>
              <ElCheckbox label="食管癌">食管癌</ElCheckbox>
              <ElCheckbox label="胰腺癌">胰腺癌</ElCheckbox>
              <ElCheckbox label="前列腺癌">前列腺癌</ElCheckbox>
              <ElCheckbox label="甲状腺癌">甲状腺癌</ElCheckbox>
              <ElCheckbox label="无家族肿瘤史">无家族肿瘤史</ElCheckbox>
            </div>
          </ElCheckboxGroup>
        </div>
      </ElFormItem>

      <!-- 家族关系详情 -->
      <ElRow v-if="formData.familyCancerHistory.length > 0 && !formData.familyCancerHistory.includes('无家族肿瘤史')" :gutter="20">
        <ElCol :span="24">
          <ElFormItem label="患病亲属关系">
            <ElCheckboxGroup v-model="formData.familyRelation">
              <ElCheckbox label="父亲">父亲</ElCheckbox>
              <ElCheckbox label="母亲">母亲</ElCheckbox>
              <ElCheckbox label="兄弟">兄弟</ElCheckbox>
              <ElCheckbox label="姐妹">姐妹</ElCheckbox>
              <ElCheckbox label="祖父">祖父</ElCheckbox>
              <ElCheckbox label="祖母">祖母</ElCheckbox>
              <ElCheckbox label="外祖父">外祖父</ElCheckbox>
              <ElCheckbox label="外祖母">外祖母</ElCheckbox>
            </ElCheckboxGroup>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider />

      <!-- 手术史 -->
      <ElFormItem label="手术史" prop="hasSurgery">
        <ElRadioGroup v-model="formData.hasSurgery">
          <ElRadio :label="false">无</ElRadio>
          <ElRadio :label="true">有</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElRow v-if="formData.hasSurgery" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="手术名称" prop="surgeryName">
            <ElInput v-model="formData.surgeryName" placeholder="请输入手术名称" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="手术时间" prop="surgeryDate">
            <ElDatePicker
              v-model="formData.surgeryDate"
              type="date"
              placeholder="请选择手术时间"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider />

      <!-- 长期用药 -->
      <ElFormItem label="长期用药">
        <ElCheckboxGroup v-model="formData.longTermMedication">
          <ElCheckbox label="降压药">降压药</ElCheckbox>
          <ElCheckbox label="降糖药">降糖药</ElCheckbox>
          <ElCheckbox label="免疫抑制剂">免疫抑制剂</ElCheckbox>
          <ElCheckbox label="激素类药物">激素类药物</ElCheckbox>
          <ElCheckbox label="无">无</ElCheckbox>
        </ElCheckboxGroup>
      </ElFormItem>

      <ElRow v-if="formData.longTermMedication.some(item => !['无'].includes(item))" :gutter="20">
        <ElCol :span="24">
          <ElFormItem label="其他药物">
            <ElInput
              v-model="formData.otherMedication"
              placeholder="如有其他长期用药，请填写"
              type="textarea"
              :rows="2"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider content-position="left">
        <span style="color: var(--el-color-primary); font-weight: 600;">🏭 环境与职业暴露（V2.0新增）</span>
      </ElDivider>

      <!-- 职业暴露 -->
      <ElFormItem label="职业暴露史" prop="hasOccupationalExposure">
        <ElRadioGroup v-model="formData.hasOccupationalExposure">
          <ElRadio :label="false">无</ElRadio>
          <ElRadio :label="true">有</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElRow v-if="formData.hasOccupationalExposure" :gutter="20">
        <ElCol :span="24">
          <ElFormItem label="暴露类型" prop="occupationalExposureTypes">
            <ElCheckboxGroup v-model="formData.occupationalExposureTypes">
              <ElCheckbox label="化学品">化学品（苯、甲醛等）</ElCheckbox>
              <ElCheckbox label="粉尘">粉尘（石棉、矽尘等）</ElCheckbox>
              <ElCheckbox label="辐射">辐射（X射线、核辐射等）</ElCheckbox>
              <ElCheckbox label="生物因子">生物因子（病毒、细菌等）</ElCheckbox>
              <ElCheckbox label="重金属">重金属（铅、汞、镉等）</ElCheckbox>
              <ElCheckbox label="其他">其他</ElCheckbox>
            </ElCheckboxGroup>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <!-- 环境因素 -->
      <ElFormItem label="居住环境空气质量" prop="airQuality">
        <ElRadioGroup v-model="formData.airQuality">
          <ElRadio label="很好">很好</ElRadio>
          <ElRadio label="良好">良好</ElRadio>
          <ElRadio label="一般">一般</ElRadio>
          <ElRadio label="差">差</ElRadio>
          <ElRadio label="很差">很差</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElFormItem label="污染暴露" prop="hasPollutionExposure">
        <ElRadioGroup v-model="formData.hasPollutionExposure">
          <ElRadio :label="false">无明显污染</ElRadio>
          <ElRadio :label="true">有污染暴露</ElRadio>
        </ElRadioGroup>
        <div class="field-tip">
          <i class="el-icon-info"></i>
          如：工业废气、汽车尾气、二手烟等长期暴露
        </div>
      </ElFormItem>

      <!-- 居住环境类型 -->
      <ElFormItem label="居住环境类型" prop="livingEnvironment">
        <ElRadioGroup v-model="formData.livingEnvironment">
          <ElRadio label="城市">城市</ElRadio>
          <ElRadio label="农村">农村</ElRadio>
          <ElRadio label="工业区">工业区</ElRadio>
          <ElRadio label="郊区">郊区</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElDivider 
        v-if="formData.gender === '女'" 
        content-position="left"
      >
        <span style="color: var(--el-color-primary); font-weight: 600;">👩 女性特有因素（V2.0新增）</span>
      </ElDivider>

      <template v-if="formData.gender === '女'">
        <!-- 月经状况 -->
        <ElFormItem label="月经状况" prop="menstrualStatus">
          <ElRadioGroup v-model="formData.menstrualStatus">
            <ElRadio label="正常">正常</ElRadio>
            <ElRadio label="异常">异常（不规律/经量异常）</ElRadio>
            <ElRadio label="已绝经">已绝经</ElRadio>
          </ElRadioGroup>
        </ElFormItem>

        <!-- 妊娠史 -->
        <ElFormItem label="妊娠次数" prop="pregnancyCount">
          <ElInputNumber
            v-model="formData.pregnancyCount"
            :min="0"
            :max="20"
            placeholder="请输入妊娠次数"
            style="width: 100%"
          >
            <template #append>次</template>
          </ElInputNumber>
        </ElFormItem>

        <ElRow v-if="formData.pregnancyCount && formData.pregnancyCount > 0" :gutter="20">
          <ElCol :span="12">
            <ElFormItem label="首次妊娠年龄" prop="firstPregnancyAge">
              <ElInputNumber
                v-model="formData.firstPregnancyAge"
                :min="10"
                :max="60"
                placeholder="请输入首次妊娠年龄"
                style="width: 100%"
              >
                <template #append>岁</template>
              </ElInputNumber>
            </ElFormItem>
          </ElCol>
        </ElRow>

        <!-- 哺乳史 -->
        <ElFormItem label="哺乳史" prop="hasBreastfed">
          <ElRadioGroup v-model="formData.hasBreastfed">
            <ElRadio :label="false">未哺乳</ElRadio>
            <ElRadio :label="true">有哺乳</ElRadio>
          </ElRadioGroup>
        </ElFormItem>

        <ElRow v-if="formData.hasBreastfed" :gutter="20">
          <ElCol :span="12">
            <ElFormItem label="累计哺乳时长" prop="breastfeedingMonths">
              <ElInputNumber
                v-model="formData.breastfeedingMonths"
                :min="0"
                :max="120"
                placeholder="请输入累计哺乳时长"
                style="width: 100%"
              >
                <template #append>月</template>
              </ElInputNumber>
            </ElFormItem>
          </ElCol>
        </ElRow>

        <!-- 激素治疗史 -->
        <ElFormItem label="激素治疗史">
          <ElCheckboxGroup v-model="formData.hormoneTherapyTypes">
            <ElCheckbox label="contraceptive">口服避孕药</ElCheckbox>
            <ElCheckbox label="hrt">激素替代疗法（HRT）</ElCheckbox>
            <ElCheckbox label="none">无</ElCheckbox>
          </ElCheckboxGroup>
        </ElFormItem>

        <ElRow v-if="formData.hormoneTherapyTypes.some(item => !['none'].includes(item))" :gutter="20">
          <ElCol :span="12">
            <ElFormItem label="使用年限" prop="hormoneTherapyYears">
              <ElInputNumber
                v-model="formData.hormoneTherapyYears"
                :min="0"
                :max="50"
                placeholder="请输入使用年限"
                style="width: 100%"
              >
                <template #append>年</template>
              </ElInputNumber>
            </ElFormItem>
          </ElCol>
        </ElRow>
      </template>
    </ElForm>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import type { FormRules } from 'element-plus'

interface FormData {
  chronicDiseases: string[]
  hepatitisType: string[]
  familyCancerHistory: string[]
  familyRelation: string[]
  hasSurgery: boolean
  surgeryName: string
  surgeryDate: string
  longTermMedication: string[]
  otherMedication: string
  // V2.0 新增：环境与职业暴露
  hasOccupationalExposure: boolean
  occupationalExposureTypes: string[]
  airQuality: string
  hasPollutionExposure: boolean
  livingEnvironment: string
  // V2.0 新增：女性特有因素
  gender?: string
  menstrualStatus: string
  pregnancyCount: number | null
  firstPregnancyAge: number | null
  hasBreastfed: boolean
  breastfeedingMonths: number | null
  hormoneTherapyTypes: string[]
  hormoneTherapyYears: number | null
}

const formData = defineModel<FormData>('formData', { required: true })

// 表单验证规则
const rules: FormRules = {
  hasSurgery: [{ required: true, message: '请选择是否有手术史', trigger: 'change' }],
  surgeryName: [
    { required: true, message: '请输入手术名称', trigger: 'blur' }
  ],
  surgeryDate: [
    { required: true, message: '请选择手术时间', trigger: 'change' }
  ],
  // V2.0 新增字段验证
  hasOccupationalExposure: [{ required: true, message: '请选择是否有职业暴露', trigger: 'change' }],
  airQuality: [{ required: true, message: '请选择空气质量', trigger: 'change' }],
  hasPollutionExposure: [{ required: true, message: '请选择是否有污染暴露', trigger: 'change' }],
  livingEnvironment: [{ required: true, message: '请选择居住环境类型', trigger: 'change' }]
}

// 监听"无"选项，自动取消其他选项
watch(
  () => formData.value.chronicDiseases,
  (newVal) => {
    if (newVal.includes('无') && newVal.length > 1) {
      formData.value.chronicDiseases = ['无']
    }
  }
)

watch(
  () => formData.value.familyCancerHistory,
  (newVal) => {
    if (newVal.includes('无家族肿瘤史') && newVal.length > 1) {
      formData.value.familyCancerHistory = ['无家族肿瘤史']
    }
  }
)

watch(
  () => formData.value.longTermMedication,
  (newVal) => {
    if (newVal.includes('无') && newVal.length > 1) {
      formData.value.longTermMedication = ['无']
    }
  }
)

// V2.0 新增：监听激素治疗类型
watch(
  () => formData.value.hormoneTherapyTypes,
  (newVal) => {
    if (newVal.includes('none') && newVal.length > 1) {
      formData.value.hormoneTherapyTypes = ['none']
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
  }

  .family-history-wrapper {
    width: 100%;

    .cancer-type-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 10px;
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
</style>

