"""
大模型服务 - 使用智谱GLM-4.6生成个性化健康建议
"""
from zhipuai import ZhipuAI
from typing import Dict, List, Optional, Generator
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """大语言模型服务 - 智谱GLM-4.6"""
    
    def __init__(self):
        """初始化智谱AI客户端"""
        # 从配置中获取API Key
        api_key = getattr(settings, 'ZHIPU_API_KEY', None)
        if not api_key:
            logger.warning("未配置ZHIPU_API_KEY，LLM功能将降级")
            self.client = None
        else:
            self.client = ZhipuAI(api_key=api_key)
            logger.info("智谱GLM-4.6客户端初始化成功")
        
        self.model = "glm-4-flash"  # 使用GLM-4-Flash模型（更快，免费额度更多）
    
    def generate_personalized_recommendations(
        self, 
        user_data: Dict, 
        risk_result: Dict
    ) -> Optional[str]:
        """
        生成个性化健康建议
        
        Args:
            user_data: 用户问卷数据
            risk_result: 风险评估结果
            
        Returns:
            str: AI生成的个性化建议（200-300字）
            None: 如果生成失败
        """
        if not self.client:
            logger.warning("LLM客户端未初始化，返回降级建议")
            return self._fallback_recommendation(risk_result)
        
        try:
            # 构建提示词
            prompt = self._build_prompt(user_data, risk_result)
            
            # 调用GLM-4.6
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                thinking={
                    "type": "disabled"  # 禁用深度思考，加快响应速度
                },
                temperature=0.7,  # 创造性（0-1）
                max_tokens=2048,  # 增加到2048，确保输出完整
                top_p=0.8
            )
            
            # 提取生成的文本
            message = response.choices[0].message
            ai_text = message.content.strip() if message.content else ""
            
            # 如果content为空，检查reasoning_content
            if not ai_text and hasattr(message, 'reasoning_content') and message.reasoning_content:
                logger.warning("content为空，使用reasoning_content")
                ai_text = message.reasoning_content.strip()
            
            logger.info(f"AI建议生成成功，长度: {len(ai_text)}字")
            return ai_text
            
        except Exception as e:
            logger.error(f"AI建议生成失败: {str(e)}")
            # 降级处理
            return self._fallback_recommendation(risk_result)
    
    def _build_prompt(self, user_data: Dict, risk_result: Dict) -> str:
        """构建Prompt"""
        
        # 提取关键信息
        age = user_data.get('age', 0)
        gender = user_data.get('gender', '未知')
        
        # 安全获取嵌套数据
        overall_risk = risk_result.get('overall_risk', {})
        risk_score = overall_risk.get('score', 0)
        risk_level = overall_risk.get('level', '未知')
        
        # 获取关键因素（前3个）
        key_factors = risk_result.get('key_factors', [])[:3]
        
        # 计算BMI
        height = user_data.get('height', 170)
        weight = user_data.get('weight', 60)
        bmi = weight / ((height / 100) ** 2) if height > 0 else 22
        
        # 构建因素列表
        if key_factors:
            factors_str = "\n".join([
                f"- {f.get('factor', '未知')}：{f.get('description', '')}" 
                for f in key_factors
            ])
        else:
            factors_str = "- 暂无显著风险因素"
        
        prompt = f"""你是一位专业、温和的肿瘤预防医生。请根据以下患者信息，生成个性化的健康建议。

【患者信息】
- 年龄：{age}岁
- 性别：{gender}
- BMI：{bmi:.1f}
- 综合风险评分：{risk_score*100:.0f}分（{risk_level}）

【主要风险因素】
{factors_str}

【要求】
1. 语气温和、专业，避免引起恐慌
2. 重点针对可改变的风险因素给出建议
3. 给出3-4条具体、可操作的建议
4. 包含生活方式、饮食、筛查等方面
5. 字数控制在200-300字
6. 如果是高风险，建议就医但不要过度夸大
7. 使用简洁的段落，不要使用编号列表
8. 语言要通俗易懂，避免过多医学术语

请直接生成建议内容，不要有多余的开场白或总结。"""

        return prompt
    
    def _fallback_recommendation(self, risk_result: Dict) -> str:
        """降级方案：规则生成建议"""
        overall_risk = risk_result.get('overall_risk', {})
        risk_level = overall_risk.get('level', '中风险')
        
        templates = {
            "低风险": "根据您的评估结果，目前肿瘤风险较低。建议您继续保持良好的生活习惯，均衡饮食，适量运动。定期进行健康体检，关注身体变化。如有不适，及时就医。",
            
            "中风险": "您的肿瘤风险处于中等水平。建议您注意调整生活方式：戒烟限酒，保持健康体重，增加蔬菜水果摄入。建议每年进行一次全面体检，包括相关的肿瘤筛查项目。如有家族史或不适症状，请咨询专业医生。",
            
            "高风险": "您的肿瘤风险评估结果偏高，建议您尽快到正规医院进行全面体检。在等待就医期间，请立即改善生活习惯：如果吸烟请戒烟，控制体重，规律作息。请特别关注身体的异常变化，如持续不适应立即就医。",
            
            "极高风险": "您存在多项高危因素，风险评估结果较高。强烈建议您尽快到医院肿瘤科或相关专科就诊，进行全面检查。请不要过度担心，早发现早治疗是关键。在就医前，请保持良好心态，改善生活习惯，遵医嘱进行必要的检查。"
        }
        
        return templates.get(risk_level, "建议定期体检，关注健康，如有疑虑请咨询专业医生。")
    
    def generate_comparison_summary(
        self, 
        old_assessment: Dict, 
        new_assessment: Dict
    ) -> Optional[str]:
        """
        生成历史对比总结（可选功能）
        
        Args:
            old_assessment: 旧评估数据
            new_assessment: 新评估数据
            
        Returns:
            str: AI生成的对比分析
        """
        if not self.client:
            return self._fallback_comparison(old_assessment, new_assessment)
        
        try:
            old_risk = old_assessment.get('overall_risk', {})
            new_risk = new_assessment.get('overall_risk', {})
            
            old_score = old_risk.get('score', 0)
            new_score = new_risk.get('score', 0)
            
            old_date = old_assessment.get('created_at', '较早')
            new_date = new_assessment.get('created_at', '最近')
            
            change = (new_score - old_score) * 100
            change_direction = '上升' if change > 0 else '下降'
            
            prompt = f"""作为健康顾问，分析患者两次肿瘤筛查的变化：

第一次评估（{old_date}）：
- 风险分数：{old_score*100:.0f}分

第二次评估（{new_date}）：
- 风险分数：{new_score*100:.0f}分
- 变化：{change_direction}{abs(change):.0f}分

请用100-150字总结变化情况，并给出鼓励或建议。语气温和积极，不要使用编号。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                thinking={
                    "type": "disabled"  # 禁用深度思考
                },
                temperature=0.7,
                max_tokens=1024
            )
            
            # 获取响应内容
            message = response.choices[0].message
            summary_text = message.content.strip() if message.content else ""
            
            # 如果content为空，使用降级方案
            if not summary_text:
                logger.warning("对比总结content为空，使用降级方案")
                return self._fallback_comparison(old_assessment, new_assessment)
            
            return summary_text
            
        except Exception as e:
            logger.error(f"对比总结生成失败: {str(e)}")
            return self._fallback_comparison(old_assessment, new_assessment)
    
    def _fallback_comparison(
        self, 
        old_assessment: Dict, 
        new_assessment: Dict
    ) -> str:
        """降级对比总结"""
        old_score = old_assessment.get('overall_risk', {}).get('score', 0)
        new_score = new_assessment.get('overall_risk', {}).get('score', 0)
        change = (new_score - old_score) * 100
        
        if abs(change) < 3:
            return "您的风险分数基本保持稳定，请继续保持良好的生活习惯。"
        elif change > 0:
            return f"您的风险分数上升了{change:.0f}分，建议重视生活方式的调整，必要时咨询医生。"
        else:
            return f"恭喜！您的风险分数下降了{abs(change):.0f}分，说明您的努力有了成效，请继续保持！"
    
    def generate_personalized_recommendations_stream(
        self, 
        user_data: Dict, 
        risk_result: Dict
    ) -> Generator[str, None, None]:
        """
        流式生成个性化健康建议（SSE）
        
        Args:
            user_data: 用户问卷数据
            risk_result: 风险评估结果
            
        Yields:
            str: 逐字生成的文本内容
        """
        if not self.client:
            logger.warning("LLM客户端未初始化，返回降级建议")
            yield self._fallback_recommendation(risk_result)
            return
        
        try:
            # 构建提示词
            prompt = self._build_prompt(user_data, risk_result)
            
            # 调用GLM-4.6（流式）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                thinking={
                    "type": "disabled"  # 禁用深度思考
                },
                stream=True,  # 启用流式输出
                temperature=0.7,
                max_tokens=2048,
                top_p=0.8
            )
            
            # 流式返回内容
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
            
            logger.info("AI建议流式生成完成")
            
        except Exception as e:
            logger.error(f"AI建议流式生成失败: {str(e)}")
            # 降级处理
            yield self._fallback_recommendation(risk_result)
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.client:
            logger.error("LLM客户端未初始化")
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "你好，请回复'连接成功'"}
                ],
                thinking={
                    "type": "disabled"
                },
                max_tokens=100
            )
            
            result = response.choices[0].message.content if response.choices[0].message.content else "无回复"
            logger.info(f"API连接测试成功: {result}")
            return True
            
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return False


# 全局实例
llm_service = LLMService()

