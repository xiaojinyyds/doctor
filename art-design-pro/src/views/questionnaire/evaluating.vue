<template>
  <div class="evaluating-container">
    <ElCard class="evaluating-card" shadow="hover">
      <div class="evaluating-content">
        <!-- 动画图标 -->
        <div class="loading-icon">
          <div class="spinner">
            <i class="iconfont-sys">&#xe7a3;</i>
          </div>
        </div>

        <!-- 进度文字 -->
        <h2 class="evaluating-title">AI正在分析您的数据...</h2>
        <p class="evaluating-desc">这可能需要几秒钟时间，请稍候</p>

        <!-- 进度步骤 -->
        <div class="progress-steps">
          <div
            v-for="(step, index) in progressSteps"
            :key="index"
            class="progress-step"
            :class="{ active: currentProgressStep >= index, completed: currentProgressStep > index }"
          >
            <div class="step-icon">
              <i v-if="currentProgressStep > index" class="iconfont-sys">&#xe621;</i>
              <i v-else class="iconfont-sys" v-html="step.icon"></i>
            </div>
            <div class="step-text">{{ step.text }}</div>
          </div>
        </div>

        <!-- 进度条 -->
        <ElProgress
          :percentage="progress"
          :status="progress === 100 ? 'success' : undefined"
          :stroke-width="12"
          class="progress-bar"
        />

        <!-- 提示信息 -->
        <div class="tips">
          <ElAlert type="info" :closable="false" show-icon>
            <template #title>
              提示：评估过程完全自动化，不会泄露您的隐私数据
            </template>
          </ElAlert>
        </div>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const currentProgressStep = ref(0)
const progress = ref(0)

const progressSteps = [
  { icon: '&#xe7a8;', text: '接收问卷数据' },
  { icon: '&#xe7a3;', text: '特征工程处理' },
  { icon: '&#xe721;', text: 'AI模型推理' },
  { icon: '&#xe86e;', text: 'SHAP可解释性分析' },
  { icon: '&#xe7b9;', text: '生成个性化建议' },
  { icon: '&#xe621;', text: '完成评估' }
]

// 模拟评估进度
const simulateProgress = () => {
  let step = 0
  const stepDuration = 500 // 每步500ms

  const timer = setInterval(() => {
    if (step < progressSteps.length) {
      currentProgressStep.value = step
      progress.value = Math.round(((step + 1) / progressSteps.length) * 100)
      step++
    } else {
      clearInterval(timer)
      // 评估完成，跳转到报告页
      setTimeout(() => {
        const assessmentId = route.query.assessmentId || 'demo-assessment-id'
        router.push(`/report/${assessmentId}`)
      }, 500)
    }
  }, stepDuration)
}

onMounted(() => {
  simulateProgress()
})
</script>

<style scoped lang="scss">
.evaluating-container {
  min-height: calc(100vh - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  .evaluating-card {
    max-width: 800px;
    width: 100%;

    :deep(.el-card__body) {
      padding: 60px 40px;
    }
  }

  .evaluating-content {
    text-align: center;

    .loading-icon {
      margin-bottom: 30px;

      .spinner {
        width: 100px;
        height: 100px;
        margin: 0 auto;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse 2s ease-in-out infinite;

        .iconfont-sys {
          font-size: 50px;
          color: #fff;
          animation: rotate 3s linear infinite;
        }
      }
    }

    .evaluating-title {
      margin: 0 0 10px 0;
      font-size: 28px;
      color: var(--art-text-gray-800);
    }

    .evaluating-desc {
      margin: 0 0 40px 0;
      color: var(--art-text-gray-500);
      font-size: 14px;
    }

    .progress-steps {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 40px;

      .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        padding: 15px;
        background: var(--art-bg-gray-100);
        border-radius: 8px;
        transition: all 0.3s;

        &.active {
          background: rgba(24, 144, 255, 0.1);

          .step-icon {
            background: var(--el-color-primary);
            color: #fff;
          }
        }

        &.completed {
          .step-icon {
            background: #52c41a;
            color: #fff;
          }
        }

        .step-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #e5e5e5;
          color: #999;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s;

          .iconfont-sys {
            font-size: 20px;
          }
        }

        .step-text {
          font-size: 13px;
          color: var(--art-text-gray-600);
        }
      }
    }

    .progress-bar {
      margin-bottom: 30px;
    }

    .tips {
      max-width: 500px;
      margin: 0 auto;
    }
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(102, 126, 234, 0);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 响应式
@media (max-width: 768px) {
  .evaluating-container {
    .evaluating-card {
      :deep(.el-card__body) {
        padding: 40px 20px;
      }
    }

    .evaluating-content {
      .progress-steps {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  }
}
</style>

