<template>
  <ElCard class="ai-recommendation-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-icon">
          <i class="iconfont-sys">&#xe7bb;</i>
        </div>
        <div class="header-content">
          <h3>🤖 AI个性化健康建议</h3>
          <p class="subtitle">由 DeepSeek 大模型智能生成</p>
        </div>
      </div>
    </template>

    <div class="recommendation-content">
      <ElSkeleton :loading="loading" :rows="5" animated>
        <template #default>
          <div v-if="recommendation" class="markdown-content" v-html="formattedRecommendation"></div>
          <ElEmpty v-else description="暂无AI建议" />
        </template>
      </ElSkeleton>
    </div>

    <div class="card-footer">
      <ElAlert type="info" :closable="false" show-icon>
        <template #title>
          本建议由AI生成，仅供参考，不能替代专业医疗诊断。如有疑虑，请及时就医。
        </template>
      </ElAlert>
    </div>
  </ElCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  recommendation?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  recommendation: '',
  loading: false
})

// 简化的 Markdown 转换为 HTML（不依赖外部库）
const formattedRecommendation = computed(() => {
  if (!props.recommendation) return ''
  
  try {
    let html = props.recommendation
    
    // 标题转换
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
    
    // 粗体
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    
    // 列表
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>')
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
    
    // 换行
    html = html.replace(/\n/g, '<br>')
    
    return html
  } catch (error) {
    console.error('Markdown解析失败:', error)
    return props.recommendation.replace(/\n/g, '<br>')
  }
})
</script>

<style scoped lang="scss">
.ai-recommendation-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;

  :deep(.el-card__header) {
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 15px;

    .header-icon {
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;

      .iconfont-sys {
        font-size: 28px;
        color: #fff;
      }
    }

    .header-content {
      flex: 1;

      h3 {
        margin: 0 0 4px 0;
        font-size: 20px;
        font-weight: 600;
        color: #fff;
      }

      .subtitle {
        margin: 0;
        font-size: 13px;
        color: rgba(255, 255, 255, 0.85);
      }
    }
  }

  .recommendation-content {
    padding: 20px;
    min-height: 200px;

    .markdown-content {
      line-height: 1.8;
      color: var(--art-text-gray-700);

      :deep(h1),
      :deep(h2),
      :deep(h3),
      :deep(h4) {
        margin: 20px 0 12px 0;
        color: var(--art-text-gray-900);
        font-weight: 600;
      }

      :deep(h1) {
        font-size: 24px;
      }

      :deep(h2) {
        font-size: 20px;
      }

      :deep(h3) {
        font-size: 18px;
      }

      :deep(h4) {
        font-size: 16px;
      }

      :deep(p) {
        margin: 12px 0;
        font-size: 15px;
      }

      :deep(ul),
      :deep(ol) {
        margin: 12px 0;
        padding-left: 24px;
      }

      :deep(li) {
        margin: 8px 0;
        font-size: 15px;
      }

      :deep(strong) {
        color: var(--el-color-primary);
        font-weight: 600;
      }

      :deep(code) {
        padding: 2px 6px;
        background: var(--el-color-info-light-9);
        border-radius: 4px;
        font-family: 'Consolas', monospace;
        font-size: 13px;
      }

      :deep(pre) {
        padding: 12px;
        background: var(--art-text-gray-100);
        border-radius: 8px;
        overflow-x: auto;
        margin: 12px 0;

        code {
          background: transparent;
          padding: 0;
        }
      }

      :deep(blockquote) {
        margin: 12px 0;
        padding: 12px 16px;
        border-left: 4px solid var(--el-color-primary);
        background: var(--el-color-primary-light-9);
        border-radius: 4px;

        p {
          margin: 0;
        }
      }
    }
  }

  .card-footer {
    padding: 0 20px 20px 20px;
  }
}
</style>

