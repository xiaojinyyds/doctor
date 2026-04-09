<template>
  <div class="screening-guide">
    <ElCard shadow="hover" class="guide-card">
      <div class="guide-header">
        <div class="guide-icon">
          <i class="iconfont-sys">&#xe788;</i>
        </div>
        <h2>开始肿瘤风险筛查</h2>
        <p>通过智能问卷快速评估您的肿瘤风险</p>
      </div>

      <div class="guide-steps">
        <div class="step-item">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>填写健康问卷</h3>
            <p>4步问卷，约3-5分钟</p>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>AI智能分析</h3>
            <p>机器学习模型评估</p>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>生成风险报告</h3>
            <p>可视化报告+健康建议</p>
          </div>
        </div>
      </div>

      <div class="guide-actions">
        <ElButton type="primary" size="large" @click="startScreening">
          <i class="iconfont-sys">&#xe788;</i>
          开始新筛查
        </ElButton>
        <ElButton size="large" @click="viewHistory">
          <i class="iconfont-sys">&#xe7b5;</i>
          查看历史记录
        </ElButton>
      </div>
    </ElCard>

    <!-- 快速统计 -->
    <ElRow :gutter="20" class="stats-row">
      <ElCol :span="8">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <i class="iconfont-sys">&#xe7b5;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ userStats.totalScreenings }}</div>
              <div class="stat-label">总筛查次数</div>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :span="8">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <i class="iconfont-sys">&#xe86e;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ userStats.lastRiskLevel }}</div>
              <div class="stat-label">最近风险等级</div>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :span="8">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <i class="iconfont-sys">&#xe7a3;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ userStats.lastScreeningDate }}</div>
              <div class="stat-label">最近筛查时间</div>
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 健康提示 -->
    <ElCard shadow="hover" class="tips-card">
      <template #header>
        <div class="card-header">
          <i class="iconfont-sys">&#xe86e;</i>
          <span>健康提示</span>
        </div>
      </template>
      <div class="tips-content">
        <ElAlert type="info" :closable="false" show-icon>
          <template #title>
            <strong>早发现、早诊断、早治疗</strong>是提高肿瘤治愈率的关键
          </template>
        </ElAlert>
        <ul class="tips-list">
          <li>建议每年进行一次健康筛查</li>
          <li>保持健康的生活方式可有效降低风险</li>
          <li>如有异常症状，请及时就医</li>
          <li>本系统仅提供风险评估参考，不构成医疗诊断</li>
        </ul>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 用户统计数据
const userStats = reactive({
  totalScreenings: 0,
  lastRiskLevel: '暂无',
  lastScreeningDate: '暂无'
})

// TODO: 从API获取用户统计数据
// onMounted(async () => {
//   const stats = await getUserStats()
//   Object.assign(userStats, stats)
// })

const startScreening = () => {
  router.push('/questionnaire/fill')
}

const viewHistory = () => {
  router.push('/history/list')
}
</script>

<style scoped lang="scss">
.screening-guide {
  .guide-card {
    margin-bottom: 20px;

    .guide-header {
      text-align: center;
      padding: 20px 0;

      .guide-icon {
        margin-bottom: 20px;

        .iconfont-sys {
          font-size: 72px;
          color: var(--el-color-primary);
        }
      }

      h2 {
        margin: 0 0 10px 0;
        font-size: 28px;
        color: var(--art-text-gray-800);
      }

      p {
        margin: 0;
        color: var(--art-text-gray-500);
        font-size: 14px;
      }
    }

    .guide-steps {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 40px 20px;
      gap: 20px;

      .step-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 20px;
        background: var(--art-bg-gray-100);
        border-radius: 12px;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .step-number {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: var(--el-color-primary);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          font-weight: bold;
        }

        .step-content {
          h3 {
            margin: 0 0 5px 0;
            font-size: 16px;
            color: var(--art-text-gray-800);
          }

          p {
            margin: 0;
            font-size: 13px;
            color: var(--art-text-gray-500);
          }
        }
      }

      .step-arrow {
        font-size: 28px;
        color: var(--art-text-gray-400);
        font-weight: bold;
      }
    }

    .guide-actions {
      display: flex;
      justify-content: center;
      gap: 20px;
      padding: 20px 0;

      .el-button {
        min-width: 160px;

        .iconfont-sys {
          margin-right: 6px;
          font-size: 16px;
        }
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;

          .iconfont-sys {
            font-size: 32px;
            color: #fff;
          }
        }

        .stat-data {
          flex: 1;

          .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--art-text-gray-800);
            margin-bottom: 5px;
          }

          .stat-label {
            font-size: 13px;
            color: var(--art-text-gray-500);
          }
        }
      }
    }
  }

  .tips-card {
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;

      .iconfont-sys {
        font-size: 18px;
        color: var(--el-color-primary);
      }
    }

    .tips-content {
      .tips-list {
        margin: 15px 0 0 0;
        padding-left: 20px;

        li {
          margin-bottom: 10px;
          color: var(--art-text-gray-600);
          line-height: 1.6;
        }
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .screening-guide {
    .guide-card {
      .guide-steps {
        flex-direction: column;
        gap: 10px;

        .step-arrow {
          transform: rotate(90deg);
        }

        .step-item {
          width: 100%;
        }
      }

      .guide-actions {
        flex-direction: column;

        .el-button {
          width: 100%;
        }
      }
    }
  }
}
</style>

