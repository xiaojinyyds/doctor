"""
LLM service backed by DeepSeek chat completions.
"""

from typing import Dict, Optional, Generator
import logging

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Generate recommendations with DeepSeek and fall back to rules on failure."""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY.strip()
        self.base_url = settings.DEEPSEEK_BASE_URL.rstrip("/")
        self.model = settings.DEEPSEEK_MODEL.strip() or "deepseek-chat"

        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not configured, LLM features will fall back")
        else:
            logger.info("DeepSeek client configured successfully")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _request_chat_completion(
        self,
        prompt: str,
        stream: bool = False,
        max_tokens: int = 2048,
    ):
        if not self.enabled:
            raise RuntimeError("DeepSeek API key is not configured")

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": max_tokens,
                "top_p": 0.8,
                "stream": stream,
            },
            stream=stream,
            timeout=60,
        )
        response.raise_for_status()
        return response

    def generate_personalized_recommendations(
        self,
        user_data: Dict,
        risk_result: Dict
    ) -> Optional[str]:
        if not self.enabled:
            return self._fallback_recommendation(risk_result)

        try:
            prompt = self._build_prompt(user_data, risk_result)
            response = self._request_chat_completion(prompt, stream=False, max_tokens=2048)
            data = response.json()
            ai_text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if not ai_text:
                return self._fallback_recommendation(risk_result)
            logger.info("DeepSeek recommendation generated successfully")
            return ai_text
        except Exception as e:
            logger.error("DeepSeek recommendation failed: %s", e)
            return self._fallback_recommendation(risk_result)

    def _build_prompt(self, user_data: Dict, risk_result: Dict) -> str:
        age = user_data.get("age", 0)
        gender = user_data.get("gender", "未知")

        overall_risk = risk_result.get("overall_risk", {})
        risk_score = overall_risk.get("score", 0)
        risk_level = overall_risk.get("level", "未知")

        key_factors = risk_result.get("key_factors", [])[:3]

        height = user_data.get("height", 170)
        weight = user_data.get("weight", 60)
        bmi = weight / ((height / 100) ** 2) if height > 0 else 22

        if key_factors:
            factors_str = "\n".join(
                f"- {f.get('factor', '未知')}：{f.get('description', '')}"
                for f in key_factors
            )
        else:
            factors_str = "- 暂无显著风险因素"

        return f"""你是一位专业、温和的肿瘤预防医生。请根据以下患者信息，生成个性化的健康建议。

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

    def _fallback_recommendation(self, risk_result: Dict) -> str:
        overall_risk = risk_result.get("overall_risk", {})
        risk_level = overall_risk.get("level", "中风险")

        templates = {
            "低风险": "根据您的评估结果，目前肿瘤风险较低。建议您继续保持良好的生活习惯，均衡饮食，适量运动。定期进行健康体检，关注身体变化。如有不适，及时就医。",
            "中风险": "您的肿瘤风险处于中等水平。建议您注意调整生活方式：戒烟限酒，保持健康体重，增加蔬菜水果摄入。建议每年进行一次全面体检，包括相关的肿瘤筛查项目。如有家族史或不适症状，请咨询专业医生。",
            "高风险": "您的肿瘤风险评估结果偏高，建议您尽快到正规医院进行全面体检。在等待就医期间，请立即改善生活习惯，如有吸烟请戒烟，控制体重，规律作息。请特别关注身体的异常变化，如持续不适应立即就医。",
            "极高风险": "您存在多项高危因素，风险评估结果较高。强烈建议您尽快到医院肿瘤科或相关专科就诊，进行全面检查。请不要过度担心，早发现早治疗是关键。在就医前，请保持良好心态，改善生活习惯，遵医嘱进行必要的检查。",
        }
        return templates.get(risk_level, "建议定期体检，关注健康，如有疑虑请咨询专业医生。")

    def generate_comparison_summary(
        self,
        old_assessment: Dict,
        new_assessment: Dict
    ) -> Optional[str]:
        if not self.enabled:
            return self._fallback_comparison(old_assessment, new_assessment)

        try:
            old_risk = old_assessment.get("overall_risk", {})
            new_risk = new_assessment.get("overall_risk", {})

            old_score = old_risk.get("score", 0)
            new_score = new_risk.get("score", 0)

            old_date = old_assessment.get("created_at", "较早")
            new_date = new_assessment.get("created_at", "最近")

            change = (new_score - old_score) * 100
            change_direction = "上升" if change > 0 else "下降"

            prompt = f"""作为健康顾问，分析患者两次肿瘤筛查的变化：

第一次评估（{old_date}）：
- 风险分数：{old_score*100:.0f}分

第二次评估（{new_date}）：
- 风险分数：{new_score*100:.0f}分
- 变化：{change_direction}{abs(change):.0f}分

请用100-150字总结变化情况，并给出鼓励或建议。语气温和积极，不要使用编号。"""

            response = self._request_chat_completion(prompt, stream=False, max_tokens=1024)
            data = response.json()
            summary_text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if not summary_text:
                return self._fallback_comparison(old_assessment, new_assessment)
            return summary_text
        except Exception as e:
            logger.error("DeepSeek comparison summary failed: %s", e)
            return self._fallback_comparison(old_assessment, new_assessment)

    def _fallback_comparison(
        self,
        old_assessment: Dict,
        new_assessment: Dict
    ) -> str:
        old_score = old_assessment.get("overall_risk", {}).get("score", 0)
        new_score = new_assessment.get("overall_risk", {}).get("score", 0)
        change = (new_score - old_score) * 100

        if abs(change) < 3:
            return "您的风险分数基本保持稳定，请继续保持良好的生活习惯。"
        if change > 0:
            return f"您的风险分数上升了{change:.0f}分，建议重视生活方式的调整，必要时咨询医生。"
        return f"恭喜，您的风险分数下降了{abs(change):.0f}分，说明您的努力有了成效，请继续保持。"

    def generate_personalized_recommendations_stream(
        self,
        user_data: Dict,
        risk_result: Dict
    ) -> Generator[str, None, None]:
        if not self.enabled:
            yield self._fallback_recommendation(risk_result)
            return

        try:
            prompt = self._build_prompt(user_data, risk_result)
            response = self._request_chat_completion(prompt, stream=True, max_tokens=2048)

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = requests.models.complexjson.loads(payload)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except Exception:
                    continue
        except Exception as e:
            logger.error("DeepSeek streaming recommendation failed: %s", e)
            yield self._fallback_recommendation(risk_result)

    def test_connection(self) -> bool:
        if not self.enabled:
            logger.error("DeepSeek API key is not configured")
            return False

        try:
            response = self._request_chat_completion("你好，请回复“连接成功”", stream=False, max_tokens=32)
            data = response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info("DeepSeek connection test success: %s", result)
            return True
        except Exception as e:
            logger.error("DeepSeek connection test failed: %s", e)
            return False


llm_service = LLMService()
