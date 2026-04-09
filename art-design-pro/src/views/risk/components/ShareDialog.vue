<template>
  <ElDialog
    v-model="visible"
    title="分享评估报告"
    width="560px"
    :close-on-click-modal="false"
  >
    <div v-if="!shareResult" class="share-form">
      <ElForm :model="form" label-width="100px">
        <ElFormItem label="有效期">
          <ElSelect v-model="form.expire_days" placeholder="请选择">
            <ElOption label="7天" :value="7" />
            <ElOption label="30天" :value="30" />
            <ElOption label="永久" :value="0" />
          </ElSelect>
        </ElFormItem>
        
        <ElFormItem label="访问密码">
          <ElInput
            v-model="form.password"
            type="password"
            placeholder="选填，设置后访问需要密码"
            show-password
            maxlength="20"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            留空则不设置密码
          </div>
        </ElFormItem>
      </ElForm>
    </div>
    
    <div v-else class="share-result">
      <ElAlert type="success" :closable="false" show-icon>
        <template #title>
          <strong>分享链接已生成</strong>
        </template>
      </ElAlert>
      
      <div class="result-content">
        <!-- 分享链接 -->
        <div class="link-section">
          <div class="label">分享链接</div>
          <div class="link-box">
            <ElInput v-model="shareResult.share_url" readonly>
              <template #append>
                <ElButton @click="copyLink">
                  <i class="iconfont-sys">&#xe7a8;</i>
                  复制
                </ElButton>
              </template>
            </ElInput>
          </div>
        </div>
        
        <!-- 二维码 -->
        <div class="qr-section">
          <div class="label">扫码访问</div>
          <div class="qr-box">
            <img :src="shareResult.qr_code_url" alt="二维码" class="qr-image" />
          </div>
        </div>
        
        <!-- 分享信息 -->
        <div class="info-section">
          <ElDescriptions :column="2" border size="small">
            <ElDescriptionsItem label="有效期">
              {{ shareResult.expire_at ? formatExpireTime(shareResult.expire_at) : '永久' }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="访问密码">
              {{ shareResult.has_password ? '已设置' : '无' }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </div>
      </div>
    </div>
    
    <template #footer>
      <ElButton v-if="!shareResult" @click="close">取消</ElButton>
      <ElButton
        v-if="!shareResult"
        type="primary"
        :loading="submitting"
        @click="createShare"
      >
        生成分享链接
      </ElButton>
      <ElButton v-else type="primary" @click="close">完成</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/http'

const props = defineProps<{
  modelValue: boolean
  assessmentId: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'success'): void
}>()

const visible = ref(false)
const submitting = ref(false)
const shareResult = ref<any>(null)

const form = reactive({
  expire_days: 7,
  password: ''
})

watch(
  () => props.modelValue,
  (v) => {
    visible.value = v
    if (v) {
      // 重置表单
      form.expire_days = 7
      form.password = ''
      shareResult.value = null
    }
  },
  { immediate: true }
)

watch(visible, (v) => emit('update:modelValue', v))

/**
 * 创建分享链接
 */
async function createShare() {
  if (!props.assessmentId) {
    ElMessage.error('评估ID不存在')
    return
  }
  
  submitting.value = true
  
  try {
    const res: any = await request.post({
      url: '/api/v1/share/create',
      data: {
        assessment_id: props.assessmentId,
        expire_days: form.expire_days === 0 ? null : form.expire_days,
        password: form.password || null
      }
    })
    
    const backendData = res.data || res
    
    // 前端动态生成分享URL（Hash路由格式）
    const currentOrigin = window.location.origin  // http://localhost:5173 或 http://1.15.22.194:3000
    const shareUrl = `${currentOrigin}/#/share/${backendData.share_token}`  // Hash路由格式
    
    // 生成二维码URL
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(shareUrl)}`
    
    shareResult.value = {
      share_token: backendData.share_token,
      share_url: shareUrl,
      expire_at: backendData.expire_at,
      has_password: backendData.has_password,
      qr_code_url: qrCodeUrl
    }
    
    ElMessage.success('分享链接已生成')
    
    // 稍微延迟后发出成功事件，确保数据库事务已提交
    setTimeout(() => {
      emit('success')
    }, 100)
  } catch (error) {
    console.error('创建分享失败:', error)
    ElMessage.error('创建分享失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 复制链接
 */
async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareResult.value.share_url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    // 降级方案：使用document.execCommand
    const input = document.createElement('input')
    input.value = shareResult.value.share_url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    ElMessage.success('链接已复制到剪贴板')
  }
}

/**
 * 格式化过期时间
 */
function formatExpireTime(expireAt: string): string {
  const date = new Date(expireAt)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function close() {
  visible.value = false
}
</script>

<style scoped>
.share-form {
  padding: 10px 0;
}

.share-result {
  .result-content {
    margin-top: 20px;
    
    .link-section,
    .qr-section,
    .info-section {
      margin-bottom: 20px;
    }
    
    .label {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 10px;
      color: #606266;
    }
    
    .link-box {
      .iconfont-sys {
        margin-right: 4px;
      }
    }
    
    .qr-box {
      display: flex;
      justify-content: center;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 8px;
      
      .qr-image {
        width: 200px;
        height: 200px;
        border: 2px solid #e4e7ed;
        border-radius: 4px;
      }
    }
  }
}
</style>

