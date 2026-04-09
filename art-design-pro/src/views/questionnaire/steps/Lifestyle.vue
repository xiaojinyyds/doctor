<template>
  <div class="step-container">
    <h3 class="step-title">
      <i class="iconfont-sys">&#xe7a3;</i>
      生活习惯
    </h3>
    <p class="step-desc">请如实填写您的生活习惯信息</p>

    <ElForm :model="formData" :rules="rules" label-width="120px" class="step-form">
      <!-- 吸烟史 -->
      <ElFormItem label="吸烟史" prop="smokingStatus">
        <ElRadioGroup v-model="formData.smokingStatus">
          <ElRadio label="从不吸烟">从不吸烟</ElRadio>
          <ElRadio label="已戒烟">已戒烟</ElRadio>
          <ElRadio label="偶尔吸烟">偶尔吸烟（每周<3支）</ElRadio>
          <ElRadio label="每天吸烟">每天吸烟</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 吸烟详情 -->
      <ElRow v-if="formData.smokingStatus === '已戒烟'" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="戒烟年限" prop="quitSmokingYears">
            <ElInputNumber
              v-model="formData.quitSmokingYears"
              :min="0"
              :max="50"
              placeholder="请输入戒烟年限"
              style="width: 100%"
            >
              <template #append>年</template>
            </ElInputNumber>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow v-if="formData.smokingStatus === '每天吸烟'" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="每日吸烟量" prop="smokingAmount">
            <ElInputNumber
              v-model="formData.smokingAmount"
              :min="1"
              :max="100"
              placeholder="请输入每日吸烟量"
              style="width: 100%"
            >
              <template #append>支/天</template>
            </ElInputNumber>
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="吸烟年限" prop="smokingYears">
            <ElInputNumber
              v-model="formData.smokingYears"
              :min="1"
              :max="80"
              placeholder="请输入吸烟年限"
              style="width: 100%"
            >
              <template #append>年</template>
            </ElInputNumber>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider />

      <!-- 饮酒史 -->
      <ElFormItem label="饮酒史" prop="alcoholStatus">
        <ElRadioGroup v-model="formData.alcoholStatus">
          <ElRadio label="从不饮酒">从不饮酒</ElRadio>
          <ElRadio label="偶尔饮酒">偶尔饮酒（社交场合）</ElRadio>
          <ElRadio label="每周饮酒">每周饮酒</ElRadio>
          <ElRadio label="每天饮酒">每天饮酒</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElRow v-if="formData.alcoholStatus === '每周饮酒'" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="饮酒频率" prop="alcoholFrequency">
            <ElInputNumber
              v-model="formData.alcoholFrequency"
              :min="1"
              :max="7"
              placeholder="请输入饮酒频率"
              style="width: 100%"
            >
              <template #append>次/周</template>
            </ElInputNumber>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow v-if="formData.alcoholStatus === '每天饮酒'" :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="酒类类型" prop="alcoholType">
            <ElCheckboxGroup v-model="formData.alcoholType">
              <ElCheckbox label="白酒">白酒</ElCheckbox>
              <ElCheckbox label="啤酒">啤酒</ElCheckbox>
              <ElCheckbox label="红酒">红酒</ElCheckbox>
              <ElCheckbox label="其他">其他</ElCheckbox>
            </ElCheckboxGroup>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElDivider />

      <!-- 运动习惯 -->
      <ElFormItem label="运动习惯" prop="exerciseFrequency">
        <ElRadioGroup v-model="formData.exerciseFrequency">
          <ElRadio label="几乎不运动">几乎不运动</ElRadio>
          <ElRadio label="偶尔运动">偶尔运动（每月1-2次）</ElRadio>
          <ElRadio label="每周1-2次">每周运动1-2次</ElRadio>
          <ElRadio label="每周3次以上">每周运动3次以上</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElDivider />

      <!-- 饮食习惯 -->
      <ElFormItem label="饮食习惯" prop="dietHabits">
        <ElCheckboxGroup v-model="formData.dietHabits">
          <ElCheckbox label="经常吃腌制食品">经常吃腌制食品</ElCheckbox>
          <ElCheckbox label="偏好油炸食品">偏好油炸食品</ElCheckbox>
          <ElCheckbox label="爱吃烧烤">爱吃烧烤</ElCheckbox>
          <ElCheckbox label="高盐饮食">高盐饮食</ElCheckbox>
          <ElCheckbox label="饮食均衡">饮食均衡</ElCheckbox>
        </ElCheckboxGroup>
      </ElFormItem>

      <ElDivider />

      <!-- 睡眠质量 -->
      <ElFormItem label="睡眠时长" prop="sleepHours">
        <ElInputNumber
          v-model="formData.sleepHours"
          :min="0"
          :max="24"
          :precision="1"
          placeholder="请输入每日睡眠时长"
          style="width: 100%"
        >
          <template #append>小时/天</template>
        </ElInputNumber>
      </ElFormItem>

      <ElFormItem label="睡眠质量" prop="sleepQuality">
        <ElRadioGroup v-model="formData.sleepQuality">
          <ElRadio label="良好">良好</ElRadio>
          <ElRadio label="一般">一般</ElRadio>
          <ElRadio label="差">较差</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <ElDivider content-position="left">
        <span style="color: var(--el-color-primary); font-weight: 600;">📋 详细饮食习惯（V2.0新增）</span>
      </ElDivider>

      <!-- 蔬菜水果摄入 -->
      <ElFormItem label="蔬菜水果摄入" prop="vegetableFruitIntake">
        <ElRadioGroup v-model="formData.vegetableFruitIntake">
          <ElRadio label="每天">每天</ElRadio>
          <ElRadio label="经常">经常（每周4-6次）</ElRadio>
          <ElRadio label="偶尔">偶尔（每周1-3次）</ElRadio>
          <ElRadio label="很少">很少</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 红肉摄入 -->
      <ElFormItem label="红肉摄入" prop="redMeatIntake">
        <ElRadioGroup v-model="formData.redMeatIntake">
          <ElRadio label="每天">每天</ElRadio>
          <ElRadio label="每周2-3次">每周2-3次</ElRadio>
          <ElRadio label="每周1-2次">每周1-2次</ElRadio>
          <ElRadio label="很少">很少</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 加工食品摄入 -->
      <ElFormItem label="加工食品摄入" prop="processedFoodIntake">
        <ElRadioGroup v-model="formData.processedFoodIntake">
          <ElRadio label="每天">每天</ElRadio>
          <ElRadio label="经常">经常（每周4-6次）</ElRadio>
          <ElRadio label="偶尔">偶尔（每周1-3次）</ElRadio>
          <ElRadio label="很少">很少</ElRadio>
        </ElRadioGroup>
        <div class="field-tip">
          <i class="el-icon-info"></i>
          包括：火腿、香肠、腊肉、罐头等
        </div>
      </ElFormItem>

      <!-- 腌制食品摄入 -->
      <ElFormItem label="腌制食品摄入" prop="pickledFoodIntake">
        <ElRadioGroup v-model="formData.pickledFoodIntake">
          <ElRadio label="每天">每天</ElRadio>
          <ElRadio label="经常">经常（每周4-6次）</ElRadio>
          <ElRadio label="偶尔">偶尔（每周1-3次）</ElRadio>
          <ElRadio label="很少">很少</ElRadio>
        </ElRadioGroup>
        <div class="field-tip">
          <i class="el-icon-info"></i>
          包括：咸菜、泡菜、腌肉、咸鱼等
        </div>
      </ElFormItem>

      <!-- 乳制品摄入 -->
      <ElFormItem label="乳制品摄入" prop="dairyIntake">
        <ElRadioGroup v-model="formData.dairyIntake">
          <ElRadio label="每天">每天</ElRadio>
          <ElRadio label="经常">经常（每周4-6次）</ElRadio>
          <ElRadio label="偶尔">偶尔（每周1-3次）</ElRadio>
          <ElRadio label="很少">很少</ElRadio>
        </ElRadioGroup>
        <div class="field-tip">
          <i class="el-icon-info"></i>
          包括：牛奶、酸奶、奶酪等
        </div>
      </ElFormItem>

      <ElDivider content-position="left">
        <span style="color: var(--el-color-primary); font-weight: 600;">🧘 精神压力与作息（V2.0新增）</span>
      </ElDivider>

      <!-- 压力水平 -->
      <ElFormItem label="压力水平" prop="stressLevel">
        <ElRadioGroup v-model="formData.stressLevel">
          <ElRadio label="低">低（生活轻松）</ElRadio>
          <ElRadio label="中">中（偶有压力）</ElRadio>
          <ElRadio label="高">高（经常焦虑）</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 作息规律性 -->
      <ElFormItem label="作息规律性" prop="workRestPattern">
        <ElRadioGroup v-model="formData.workRestPattern">
          <ElRadio label="规律">规律（固定作息）</ElRadio>
          <ElRadio label="一般">一般（偶尔不规律）</ElRadio>
          <ElRadio label="不规律">不规律</ElRadio>
          <ElRadio label="经常熬夜">经常熬夜</ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 心理健康 -->
      <ElFormItem label="心理健康状况" prop="mentalHealth">
        <ElRadioGroup v-model="formData.mentalHealth">
          <ElRadio label="良好">良好</ElRadio>
          <ElRadio label="一般">一般</ElRadio>
          <ElRadio label="焦虑">有焦虑倾向</ElRadio>
          <ElRadio label="抑郁">有抑郁倾向</ElRadio>
        </ElRadioGroup>
      </ElFormItem>
    </ElForm>
  </div>
</template>

<script setup lang="ts">
import type { FormRules } from 'element-plus'

interface FormData {
  smokingStatus: string
  quitSmokingYears: number | null
  smokingAmount: number | null
  smokingYears: number | null
  alcoholStatus: string
  alcoholFrequency: number | null
  alcoholType: string[]
  exerciseFrequency: string
  dietHabits: string[]
  sleepHours: number | null
  sleepQuality: string
  // V2.0 新增：详细饮食习惯
  vegetableFruitIntake: string
  redMeatIntake: string
  processedFoodIntake: string
  pickledFoodIntake: string
  dairyIntake: string
  // V2.0 新增：精神压力与作息
  stressLevel: string
  workRestPattern: string
  mentalHealth: string
}

const formData = defineModel<FormData>('formData', { required: true })

// 表单验证规则
const rules: FormRules = {
  smokingStatus: [{ required: true, message: '请选择吸烟史', trigger: 'change' }],
  alcoholStatus: [{ required: true, message: '请选择饮酒史', trigger: 'change' }],
  exerciseFrequency: [{ required: true, message: '请选择运动习惯', trigger: 'change' }],
  sleepHours: [{ required: true, message: '请输入每日睡眠时长', trigger: 'blur' }],
  sleepQuality: [{ required: true, message: '请选择睡眠质量', trigger: 'change' }],
  // V2.0 新增字段验证
  vegetableFruitIntake: [{ required: true, message: '请选择蔬菜水果摄入频率', trigger: 'change' }],
  redMeatIntake: [{ required: true, message: '请选择红肉摄入频率', trigger: 'change' }],
  processedFoodIntake: [{ required: true, message: '请选择加工食品摄入频率', trigger: 'change' }],
  pickledFoodIntake: [{ required: true, message: '请选择腌制食品摄入频率', trigger: 'change' }],
  dairyIntake: [{ required: true, message: '请选择乳制品摄入频率', trigger: 'change' }],
  stressLevel: [{ required: true, message: '请选择压力水平', trigger: 'change' }],
  workRestPattern: [{ required: true, message: '请选择作息规律性', trigger: 'change' }],
  mentalHealth: [{ required: true, message: '请选择心理健康状况', trigger: 'change' }]
}

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
    :deep(.el-radio),
    :deep(.el-checkbox) {
      margin-right: 20px;
      margin-bottom: 12px;
    }

    :deep(.el-input-number) {
      width: 100%;
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

