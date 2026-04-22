<template>
  <ElDialog 
    v-model="visible" 
    title="风险评估申请" 
    width="680px" 
    :close-on-click-modal="false"
    class="assessment-apply-dialog"
  >
    <div class="dialog-content">
      <ElAlert type="info" :closable="false" show-icon>
        <template #title>
          <strong>增强版评估</strong> - 采用XGBoost机器学习模型，准确率81.21%
        </template>
      </ElAlert>

      <div class="assessment-intro">
        <div class="intro-header">
          <i class="iconfont-sys">&#xe788;</i>
          <h3>完整问卷评估（推荐）</h3>
          <ElTag type="success" effect="dark">增强版</ElTag>
        </div>
        <p class="intro-desc">
          通过4步完整问卷，收集32个关键特征，提供：
        </p>
        <ul class="feature-list">
          <li><i class="el-icon-check"></i> 基于XGBoost的精准风险预测</li>
          <li><i class="el-icon-check"></i> SHAP可解释性分析</li>
          <li><i class="el-icon-check"></i> DeepSeek AI个性化健康建议</li>
          <li><i class="el-icon-check"></i> 详细的饮食、压力、环境因素分析</li>
          <li><i class="el-icon-check"></i> 女性特有因素评估</li>
        </ul>
        <div class="intro-actions">
          <ElButton type="primary" size="large" @click="goToFullQuestionnaire">
            <i class="iconfont-sys">&#xe621;</i>
            开始完整评估
          </ElButton>
        </div>
      </div>

      <ElDivider>或</ElDivider>

      <div class="quick-assessment">
        <div class="quick-header">
          <i class="iconfont-sys">&#xe7a2;</i>
          <h3>快速评估（简化版）</h3>
          <ElTag type="warning" effect="plain">基础版</ElTag>
        </div>
        <p class="quick-desc">
          仅填写基础信息，快速获取初步评估结果（准确性相对较低）
        </p>

        <ElForm ref="formRef" :model="form" :rules="rules" label-width="110px" size="default">
          <ElRow :gutter="20">
            <ElCol :span="12">
              <ElFormItem label="年龄" prop="age">
                <ElInputNumber v-model="form.age" :min="18" :max="120" style="width: 100%" />
              </ElFormItem>
            </ElCol>
            <ElCol :span="12">
              <ElFormItem label="性别" prop="gender">
                <ElSelect v-model="form.gender" style="width: 100%">
                  <ElOption label="男" value="男" />
                  <ElOption label="女" value="女" />
                </ElSelect>
              </ElFormItem>
            </ElCol>
          </ElRow>

          <ElRow :gutter="20">
            <ElCol :span="12">
              <ElFormItem label="身高(cm)" prop="height">
                <ElInputNumber v-model="form.height" :min="100" :max="250" style="width: 100%" />
              </ElFormItem>
            </ElCol>
            <ElCol :span="12">
              <ElFormItem label="体重(kg)" prop="weight">
                <ElInputNumber v-model="form.weight" :min="30" :max="200" :precision="1" style="width: 100%" />
              </ElFormItem>
            </ElCol>
          </ElRow>

          <ElRow :gutter="20">
            <ElCol :span="12">
              <ElFormItem label="吸烟状态" prop="smoking">
                <ElSelect v-model="form.smoking" style="width: 100%">
                  <ElOption label="从不吸烟" :value="0" />
                  <ElOption label="曾经吸烟" :value="1" />
                  <ElOption label="目前吸烟" :value="2" />
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :span="12">
              <ElFormItem label="运动(小时/周)" prop="physical_activity">
                <ElInputNumber v-model="form.physical_activity" :min="0" :max="50" :step="0.5" style="width: 100%" />
              </ElFormItem>
            </ElCol>
          </ElRow>

          <ElFormItem label="家族肿瘤史" prop="family_history">
            <ElSelect
              v-model="form.family_history"
              multiple
              placeholder="请选择（可多选）"
              style="width: 100%"
            >
              <ElOption label="肺癌" value="肺癌" />
              <ElOption label="胃癌" value="胃癌" />
              <ElOption label="肝癌" value="肝癌" />
              <ElOption label="结直肠癌" value="结直肠癌" />
              <ElOption label="乳腺癌" value="乳腺癌" />
              <ElOption label="其他癌症" value="其他" />
            </ElSelect>
          </ElFormItem>
        </ElForm>

        <div class="quick-warning">
          <ElAlert type="warning" :closable="false" show-icon>
            <template #title>
              简化评估仅供参考，建议使用完整问卷获取更准确的评估结果
            </template>
          </ElAlert>
        </div>
      </div>
    </div>

    <template #footer>
      <ElButton @click="close">取消</ElButton>
      <ElButton type="default" :loading="submitting" @click="submitQuick">
        快速评估（简化版）
      </ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { ref, reactive, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'
  import { submitAssessment, type AssessmentSubmitPayload } from '@/api/assessment'
  import { useUserStore } from '@/store/modules/user'

  const props = defineProps<{ modelValue: boolean }>()
  const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'submitted'): void }>()

  const router = useRouter()
  const visible = ref(false)
  
  watch(
    () => props.modelValue,
    (v) => (visible.value = v),
    { immediate: true }
  )
  watch(visible, (v) => emit('update:modelValue', v))

  const formRef = ref<FormInstance>()
  const form = reactive<AssessmentSubmitPayload>({
    age: 45,
    alcohol_intake: 0,
    cancer_history: 0,
    chronic_diseases: [],
    family_history: [],
    gender: '男',
    genetic_risk: 0,
    height: 170,
    notes: '',
    physical_activity: 0,
    smoking: 0,
    symptoms: [],
    weight: 60
  })

  const rules: FormRules = {
    age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
    gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
    height: [{ required: true, message: '请输入身高', trigger: 'blur' }],
    weight: [{ required: true, message: '请输入体重', trigger: 'blur' }]
  }

  const submitting = ref(false)
  
  function close() {
    visible.value = false
  }

  // 跳转到完整问卷
  function goToFullQuestionnaire() {
    console.log('准备跳转到完整问卷页面...')
    
    // 调试：打印用户角色信息
    const userStore = useUserStore()
    console.log('当前用户角色:', userStore.info?.roles)
    
    // 调试：打印所有已注册的路由
    const allRoutes = router.getRoutes()
    console.log('所有已注册路由数量:', allRoutes.length)
    
    // 查找问卷相关路由
    const questionnaireRoute = allRoutes.find(r => r.path === '/questionnaire' || r.name === 'Questionnaire')
    if (questionnaireRoute) {
      console.log('找到问卷路由:', questionnaireRoute)
    } else {
      console.warn('未找到问卷路由！')
      console.log('已注册的路由列表:', allRoutes.map(r => ({ name: r.name, path: r.path })))
    }
    
    // 跳转到问卷页面
    router.push('/questionnaire')
      .then(() => {
        console.log('路由跳转成功')
        close()
      })
      .catch((err) => {
        console.error('路由跳转失败:', err)
        ElMessage.error('页面跳转失败，请检查路由配置')
      })
  }

  // 快速评估（简化版）
  async function submitQuick() {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      submitting.value = true
      await submitAssessment({ ...form })
      ElMessage.success('快速评估提交成功')
      emit('submitted')
      close()
    } catch (e) {
      console.error('[Assessment] submit error:', e)
      ElMessage.error('提交失败，请重试')
    } finally {
      submitting.value = false
    }
  }
</script>

<style scoped lang="scss">
.assessment-apply-dialog {
  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }

  .dialog-content {
    .assessment-intro {
      padding: 20px;
      background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
      border-radius: 12px;
      margin: 20px 0;

      .intro-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;

        .iconfont-sys {
          font-size: 32px;
          color: var(--el-color-primary);
        }

        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          flex: 1;
        }
      }

      .intro-desc {
        margin: 12px 0;
        color: var(--art-text-gray-700);
        font-size: 14px;
      }

      .feature-list {
        list-style: none;
        padding: 0;
        margin: 16px 0;

        li {
          padding: 8px 0;
          color: var(--art-text-gray-800);
          font-size: 14px;
          display: flex;
          align-items: center;
          gap: 8px;

          i {
            color: var(--el-color-success);
            font-weight: bold;
          }
        }
      }

      .intro-actions {
        margin-top: 20px;
        text-align: center;

        .el-button {
          padding: 12px 32px;
          font-size: 16px;

          .iconfont-sys {
            margin-right: 6px;
          }
        }
      }
    }

    .quick-assessment {
      .quick-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;

        .iconfont-sys {
          font-size: 28px;
          color: var(--el-color-warning);
        }

        h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          flex: 1;
        }
      }

      .quick-desc {
        margin: 8px 0 16px 0;
        color: var(--art-text-gray-600);
        font-size: 13px;
      }

      .quick-warning {
        margin-top: 16px;
      }
    }
  }
}
</style>
