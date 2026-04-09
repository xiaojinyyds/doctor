<template>
  <div class="home-container">
    <!-- Hero Section - 主横幅 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">肿瘤数智化筛查系统</span>
          </h1>
          <p class="hero-subtitle">基于AI的智能肿瘤风险评估平台</p>
          <p class="hero-description">
            早发现、早诊断、早治疗 - 通过机器学习算法为您提供专业的肿瘤风险评估服务
          </p>
          <div class="hero-actions">
            <ElButton type="primary" size="large" @click="startScreening">
              <i class="iconfont-sys">&#xe788;</i>
              开始免费筛查
            </ElButton>
            <ElButton size="large" @click="viewDemo">
              <i class="iconfont-sys">&#xe7a1;</i>
              查看演示报告
            </ElButton>
          </div>
          <div class="hero-stats">
            <div class="stat-item">
              <div class="stat-number">10,000+</div>
              <div class="stat-label">累计筛查次数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">85%+</div>
              <div class="stat-label">评估准确率</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">&lt;5分钟</div>
              <div class="stat-label">完成时间</div>
            </div>
          </div>
        </div>
        <div class="hero-image">
          <div class="image-placeholder">
            <i class="iconfont-sys">&#xe7a3;</i>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section - 核心特点 -->
    <section class="features-section">
      <div class="section-header">
        <h2 class="section-title">系统特点</h2>
        <p class="section-subtitle">AI驱动的智能筛查，为您的健康保驾护航</p>
      </div>
      <div class="features-grid">
        <ElCard v-for="(feature, index) in features" :key="index" shadow="hover" class="feature-card">
          <div class="feature-icon" :style="{ background: feature.color }">
            <i class="iconfont-sys" v-html="feature.icon"></i>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
        </ElCard>
      </div>
    </section>

    <!-- Process Section - 使用流程 -->
    <section class="process-section">
      <div class="section-header">
        <h2 class="section-title">使用流程</h2>
        <p class="section-subtitle">简单4步，即可获得专业的风险评估报告</p>
      </div>
      <div class="process-timeline">
        <div v-for="(step, index) in processSteps" :key="index" class="process-step">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <div class="step-icon">
              <i class="iconfont-sys" v-html="step.icon"></i>
            </div>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-desc">{{ step.description }}</p>
          </div>
          <div v-if="index < processSteps.length - 1" class="step-arrow">
            <i class="iconfont-sys">&#xe624;</i>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Section - 技术优势 -->
    <section class="tech-section">
      <div class="section-header">
        <h2 class="section-title">技术优势</h2>
        <p class="section-subtitle">基于前沿AI技术，提供可靠的风险评估</p>
      </div>
      <ElRow :gutter="20">
        <ElCol :xs="24" :sm="12" :md="6" v-for="(tech, index) in techStack" :key="index">
          <ElCard shadow="hover" class="tech-card">
            <div class="tech-icon">
              <i class="iconfont-sys" v-html="tech.icon"></i>
            </div>
            <h4>{{ tech.name }}</h4>
            <p>{{ tech.desc }}</p>
          </ElCard>
        </ElCol>
      </ElRow>
    </section>

    <!-- CTA Section - 行动号召 -->
    <section class="cta-section">
      <ElCard shadow="hover" class="cta-card">
        <div class="cta-content">
          <h2>立即开始您的健康筛查</h2>
          <p>只需3-5分钟，即可获得专业的肿瘤风险评估报告</p>
          <ElButton type="primary" size="large" @click="startScreening">
            <i class="iconfont-sys">&#xe788;</i>
            免费开始筛查
          </ElButton>
        </div>
      </ElCard>
    </section>

    <!-- Disclaimer - 免责声明 -->
    <section class="disclaimer-section">
      <ElAlert type="warning" :closable="false" show-icon>
        <template #title>
          <strong>免责声明：</strong>
          本系统提供的风险评估结果仅供参考，不构成医疗诊断。如有健康问题，请及时就医并咨询专业医生。
        </template>
      </ElAlert>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

// 核心特点
const features = [
  {
    icon: '&#xe7a3;',
    title: 'AI智能分析',
    description: '采用XGBoost机器学习算法，准确率达85%以上',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    icon: '&#xe86e;',
    title: '可解释AI',
    description: '基于SHAP技术，清晰展示各因素对风险的影响',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    icon: '&#xe7a1;',
    title: '可视化报告',
    description: '直观的图表展示，让您轻松理解评估结果',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    icon: '&#xe7b9;',
    title: '个性化建议',
    description: '根据您的风险因素，提供定制化的健康建议',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  },
  {
    icon: '&#xe7b5;',
    title: '历史追踪',
    description: '记录每次筛查结果，追踪风险变化趋势',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    icon: '&#xe7a8;',
    title: '快速便捷',
    description: '3-5分钟完成问卷，立即获得评估报告',
    color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
  }
]

// 使用流程
const processSteps = [
  {
    icon: '&#xe788;',
    title: '填写健康问卷',
    description: '回答关于年龄、生活习惯、疾病史、症状等问题'
  },
  {
    icon: '&#xe7a3;',
    title: 'AI智能分析',
    description: '机器学习模型自动分析您的健康数据'
  },
  {
    icon: '&#xe721;',
    title: '生成评估报告',
    description: '获得详细的风险评估报告和健康建议'
  },
  {
    icon: '&#xe7b5;',
    title: '持续追踪',
    description: '定期筛查，监测风险变化趋势'
  }
]

// 技术栈
const techStack = [
  {
    icon: '&#xe7a3;',
    name: 'XGBoost',
    desc: '机器学习算法'
  },
  {
    icon: '&#xe86e;',
    name: 'SHAP',
    desc: '模型可解释性'
  },
  {
    icon: '&#xe7a1;',
    name: 'ECharts',
    desc: '数据可视化'
  },
  {
    icon: '&#xe7b9;',
    name: 'Vue 3',
    desc: '现代前端框架'
  }
]

const startScreening = () => {
  if (userStore.isLogin) {
    router.push('/questionnaire/fill')
  } else {
    router.push('/auth/login')
  }
}

const viewDemo = () => {
  router.push('/report/demo-assessment-id')
}
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  background: var(--art-main-bg-color);

  section {
    max-width: 1400px;
    margin: 0 auto;
    padding: 60px 20px;
  }

  .section-header {
    text-align: center;
    margin-bottom: 50px;

    .section-title {
      margin: 0 0 15px 0;
      font-size: 36px;
      font-weight: bold;
      color: var(--art-text-gray-800);
    }

    .section-subtitle {
      margin: 0;
      font-size: 16px;
      color: var(--art-text-gray-500);
    }
  }

  // Hero Section
  .hero-section {
    padding-top: 80px;
    padding-bottom: 80px;

    .hero-content {
      display: flex;
      align-items: center;
      gap: 60px;

      .hero-text {
        flex: 1;

        .hero-title {
          margin: 0 0 20px 0;
          font-size: 48px;
          font-weight: bold;
          line-height: 1.2;

          .gradient-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
        }

        .hero-subtitle {
          margin: 0 0 15px 0;
          font-size: 24px;
          color: var(--el-color-primary);
        }

        .hero-description {
          margin: 0 0 40px 0;
          font-size: 16px;
          color: var(--art-text-gray-600);
          line-height: 1.8;
        }

        .hero-actions {
          display: flex;
          gap: 20px;
          margin-bottom: 40px;

          .el-button {
            min-width: 160px;

            .iconfont-sys {
              margin-right: 6px;
              font-size: 16px;
            }
          }
        }

        .hero-stats {
          display: flex;
          gap: 30px;
          align-items: center;

          .stat-item {
            .stat-number {
              font-size: 32px;
              font-weight: bold;
              color: var(--el-color-primary);
              margin-bottom: 5px;
            }

            .stat-label {
              font-size: 13px;
              color: var(--art-text-gray-500);
            }
          }

          .stat-divider {
            width: 1px;
            height: 40px;
            background: var(--art-border-color);
          }
        }
      }

      .hero-image {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;

        .image-placeholder {
          width: 400px;
          height: 400px;
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
          border-radius: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 2px dashed var(--el-color-primary);

          .iconfont-sys {
            font-size: 120px;
            color: var(--el-color-primary);
            opacity: 0.3;
          }
        }
      }
    }
  }

  // Features Section
  .features-section {
    background: #fff;

    .features-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 30px;

      .feature-card {
        text-align: center;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-8px);
        }

        .feature-icon {
          width: 80px;
          height: 80px;
          margin: 0 auto 20px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;

          .iconfont-sys {
            font-size: 40px;
            color: #fff;
          }
        }

        .feature-title {
          margin: 0 0 12px 0;
          font-size: 20px;
          color: var(--art-text-gray-800);
          font-weight: 600;
        }

        .feature-desc {
          margin: 0;
          font-size: 14px;
          color: var(--art-text-gray-600);
          line-height: 1.6;
        }
      }
    }
  }

  // Process Section
  .process-section {
    .process-timeline {
      display: flex;
      justify-content: center;
      align-items: flex-start;
      gap: 20px;

      .process-step {
        flex: 1;
        max-width: 280px;
        position: relative;

        .step-number {
          position: absolute;
          top: -10px;
          left: 50%;
          transform: translateX(-50%);
          width: 36px;
          height: 36px;
          background: var(--el-color-primary);
          color: #fff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: bold;
          box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
        }

        .step-content {
          background: #fff;
          padding: 50px 20px 30px;
          border-radius: 12px;
          text-align: center;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
          transition: all 0.3s;

          &:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
          }

          .step-icon {
            margin-bottom: 15px;

            .iconfont-sys {
              font-size: 48px;
              color: var(--el-color-primary);
            }
          }

          .step-title {
            margin: 0 0 10px 0;
            font-size: 18px;
            color: var(--art-text-gray-800);
            font-weight: 600;
          }

          .step-desc {
            margin: 0;
            font-size: 14px;
            color: var(--art-text-gray-600);
            line-height: 1.6;
          }
        }

        .step-arrow {
          position: absolute;
          top: 50%;
          right: -30px;
          transform: translateY(-50%);
          font-size: 24px;
          color: var(--el-color-primary);
        }
      }
    }
  }

  // Tech Section
  .tech-section {
    background: #fff;

    .tech-card {
      text-align: center;
      height: 100%;

      .tech-icon {
        margin-bottom: 15px;

        .iconfont-sys {
          font-size: 48px;
          color: var(--el-color-primary);
        }
      }

      h4 {
        margin: 0 0 8px 0;
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

  // CTA Section
  .cta-section {
    .cta-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;

      :deep(.el-card__body) {
        padding: 60px 40px;
      }

      .cta-content {
        text-align: center;
        color: #fff;

        h2 {
          margin: 0 0 15px 0;
          font-size: 32px;
        }

        p {
          margin: 0 0 30px 0;
          font-size: 16px;
          opacity: 0.9;
        }

        .el-button {
          min-width: 200px;
          background: #fff;
          color: var(--el-color-primary);
          border: none;

          &:hover {
            background: rgba(255, 255, 255, 0.9);
          }

          .iconfont-sys {
            margin-right: 6px;
          }
        }
      }
    }
  }

  // Disclaimer
  .disclaimer-section {
    padding-top: 30px;
    padding-bottom: 30px;
  }
}

// 响应式适配
@media (max-width: 1024px) {
  .home-container {
    .hero-section {
      .hero-content {
        flex-direction: column;
        gap: 40px;

        .hero-image {
          .image-placeholder {
            width: 300px;
            height: 300px;
          }
        }
      }
    }

    .features-section {
      .features-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    .process-section {
      .process-timeline {
        flex-direction: column;
        align-items: center;

        .process-step {
          .step-arrow {
            display: none;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .home-container {
    .hero-section {
      padding-top: 40px;

      .hero-content {
        .hero-text {
          .hero-title {
            font-size: 32px;
          }

          .hero-subtitle {
            font-size: 20px;
          }

          .hero-actions {
            flex-direction: column;

            .el-button {
              width: 100%;
            }
          }

          .hero-stats {
            flex-direction: column;
            gap: 15px;

            .stat-divider {
              display: none;
            }
          }
        }
      }
    }

    .features-section {
      .features-grid {
        grid-template-columns: 1fr;
      }
    }

    .section-header {
      .section-title {
        font-size: 28px;
      }
    }
  }
}
</style>

