<template>
  <div class="health-recommendations">
    <div v-for="(rec, index) in recommendations" :key="index" class="recommendation-card">
      <ElCard shadow="hover">
        <div class="rec-header">
          <div class="rec-icon" :style="{ background: getCategoryColor(rec.category) }">
            <i class="iconfont-sys" v-html="getCategoryIcon(rec.category)"></i>
          </div>
          <div class="rec-title">
            <h3>{{ rec.title }}</h3>
            <ElTag :type="getPriorityType(rec.priority)" size="small">
              优先级{{ rec.priority }}
            </ElTag>
          </div>
        </div>
        <div class="rec-content">
          <p>{{ rec.content }}</p>
        </div>
        <div v-if="rec.actionText" class="rec-action">
          <ElButton link type="primary" @click="handleAction(rec)">
            {{ rec.actionText }}
            <i class="iconfont-sys">&#xe624;</i>
          </ElButton>
        </div>
      </ElCard>
    </div>

    <ElEmpty v-if="recommendations.length === 0" description="暂无健康建议" />
  </div>
</template>

<script setup lang="ts">
interface Recommendation {
  category: string // lifestyle/diet/screening/medical
  title: string
  content: string
  priority: number // 1-5
  actionText?: string
}

interface Props {
  recommendations: Recommendation[]
}

const props = withDefaults(defineProps<Props>(), {
  recommendations: () => []
})

const emit = defineEmits<{
  action: [recommendation: Recommendation]
}>()

// 获取分类颜色
const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    lifestyle: 'linear-gradient(135deg, #f5222d 0%, #fa8c16 100%)', // 红橙渐变
    diet: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',      // 绿色渐变
    screening: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)', // 蓝色渐变
    medical: 'linear-gradient(135deg, #fa8c16 0%, #faad14 100%)'    // 橙黄渐变
  }
  return colorMap[category] || 'linear-gradient(135deg, #999 0%, #bbb 100%)'
}

// 获取分类图标
const getCategoryIcon = (category: string): string => {
  const iconMap: Record<string, string> = {
    lifestyle: '&#xe7a3;', // 生活方式
    diet: '&#xe86e;',      // 饮食
    screening: '&#xe788;', // 筛查
    medical: '&#xe7b9;'    // 就医
  }
  return iconMap[category] || '&#xe86e;'
}

// 获取优先级类型
const getPriorityType = (priority: number): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  if (priority === 1) return 'danger'
  if (priority <= 2) return 'warning'
  return 'info'
}

const handleAction = (rec: Recommendation) => {
  emit('action', rec)
}
</script>

<style scoped lang="scss">
.health-recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;

  .recommendation-card {
    .rec-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;

      .rec-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;

        .iconfont-sys {
          font-size: 24px;
          color: #fff;
        }
      }

      .rec-title {
        flex: 1;

        h3 {
          margin: 0 0 6px 0;
          font-size: 16px;
          color: var(--art-text-gray-800);
          font-weight: 600;
        }
      }
    }

    .rec-content {
      p {
        margin: 0;
        color: var(--art-text-gray-600);
        line-height: 1.8;
        font-size: 14px;
      }
    }

    .rec-action {
      margin-top: 15px;
      padding-top: 15px;
      border-top: 1px solid var(--art-border-color);

      .el-button {
        .iconfont-sys {
          margin-left: 4px;
          font-size: 12px;
        }
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .health-recommendations {
    grid-template-columns: 1fr;
  }
}
</style>

