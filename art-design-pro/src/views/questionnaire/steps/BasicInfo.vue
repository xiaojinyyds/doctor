<template>
  <div class="step-container">
    <h3 class="step-title">
      <i class="iconfont-sys">&#xe7ae;</i>
      基本信息
    </h3>
    <p class="step-desc">请填写您的基本健康信息</p>

    <ElForm :model="formData" :rules="rules" label-width="120px" class="step-form">
      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="姓名" prop="name">
            <ElInput v-model="formData.name" placeholder="选填，用于报告个性化" clearable />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="年龄(岁)" prop="age">
            <ElInputNumber
              v-model="formData.age"
              :min="18"
              :max="120"
              placeholder="请输入年龄"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="性别" prop="gender">
            <ElRadioGroup v-model="formData.gender">
              <ElRadio label="男">男</ElRadio>
              <ElRadio label="女">女</ElRadio>
            </ElRadioGroup>
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="民族" prop="ethnicity">
            <ElSelect v-model="formData.ethnicity" placeholder="请选择民族">
              <ElOption label="汉族" value="汉族" />
              <ElOption label="少数民族" value="少数民族" />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="身高(cm)" prop="height">
            <ElInputNumber
              v-model="formData.height"
              :min="100"
              :max="250"
              :precision="1"
              placeholder="请输入身高"
              @change="calculateBMI"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="体重(kg)" prop="weight">
            <ElInputNumber
              v-model="formData.weight"
              :min="30"
              :max="200"
              :precision="1"
              placeholder="请输入体重"
              @change="calculateBMI"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="20">
        <ElCol :span="12">
          <ElFormItem label="BMI指数(kg/m²)">
            <ElInput v-model="bmiValue" disabled>
              <template #append>
                <span :style="{ color: getBMIColor() }">{{ getBMIStatus() }}</span>
              </template>
            </ElInput>
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="职业" prop="occupation">
            <ElSelect v-model="formData.occupation" placeholder="请选择职业" filterable>
              <ElOption label="企业职员" value="企业职员" />
              <ElOption label="政府机关" value="政府机关" />
              <ElOption label="教师" value="教师" />
              <ElOption label="医生" value="医生" />
              <ElOption label="工人" value="工人" />
              <ElOption label="农民" value="农民" />
              <ElOption label="个体经营" value="个体经营" />
              <ElOption label="退休人员" value="退休人员" />
              <ElOption label="学生" value="学生" />
              <ElOption label="其他" value="其他" />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>
    </ElForm>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import type { FormRules } from 'element-plus'

  interface FormData {
    name: string
    age: number | null
    gender: string
    ethnicity: string
    height: number | null
    weight: number | null
    occupation: string
  }

  const formData = defineModel<FormData>('formData', { required: true })

  // 表单验证规则
  const rules: FormRules = {
    age: [
      { required: true, message: '请输入年龄', trigger: 'blur' },
      { type: 'number', min: 18, max: 120, message: '年龄应在18-120岁之间', trigger: 'blur' }
    ],
    gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
    height: [
      { required: true, message: '请输入身高', trigger: 'blur' },
      { type: 'number', min: 100, max: 250, message: '身高应在100-250cm之间', trigger: 'blur' }
    ],
    weight: [
      { required: true, message: '请输入体重', trigger: 'blur' },
      { type: 'number', min: 30, max: 200, message: '体重应在30-200kg之间', trigger: 'blur' }
    ]
  }

  // 计算BMI
  const bmiValue = computed(() => {
    if (formData.value.height && formData.value.weight) {
      const heightInMeters = formData.value.height / 100
      const bmi = formData.value.weight / (heightInMeters * heightInMeters)
      return bmi.toFixed(1)
    }
    return ''
  })

  const calculateBMI = () => {
    // 触发响应式更新
    if (formData.value.height && formData.value.weight) {
      const heightInMeters = formData.value.height / 100
      const bmi = formData.value.weight / (heightInMeters * heightInMeters)

      // 提示BMI异常
      if (bmi < 15 || bmi > 40) {
        ElMessage.warning('BMI值异常，请核对身高体重')
      }
    }
  }

  const getBMIStatus = () => {
    const bmi = parseFloat(bmiValue.value)
    if (!bmi) return ''
    if (bmi < 18.5) return '偏瘦'
    if (bmi < 24) return '正常'
    if (bmi < 28) return '偏胖'
    return '肥胖'
  }

  const getBMIColor = () => {
    const bmi = parseFloat(bmiValue.value)
    if (!bmi) return '#999'
    if (bmi < 18.5) return '#faad14'
    if (bmi < 24) return '#52c41a'
    if (bmi < 28) return '#fa8c16'
    return '#f5222d'
  }

  defineExpose({ rules })
</script>

<style scoped lang="scss">
  .step-container {
    .step-title {
      display: flex;
      gap: 8px;
      align-items: center;
      margin: 0 0 8px;
      font-size: 20px;
      color: var(--art-text-gray-800);

      .iconfont-sys {
        font-size: 24px;
        color: var(--el-color-primary);
      }
    }

    .step-desc {
      margin: 0 0 30px;
      font-size: 14px;
      color: var(--art-text-gray-500);
    }

    .step-form {
      :deep(.el-input-number) {
        width: 100%;
      }
    }
  }
</style>
