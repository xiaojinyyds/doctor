"""
肿瘤知识图谱服务
提供疾病、症状、风险因素之间的关系数据
"""
from typing import Dict, List, Optional
import json


class KnowledgeGraphService:
    """知识图谱服务"""
    
    def __init__(self):
        """初始化知识图谱"""
        self.graph_data = self._build_knowledge_graph()
    
    def _build_knowledge_graph(self) -> Dict:
        """
        构建肿瘤知识图谱
        
        节点类型：
        - disease: 疾病（category: 0）
        - risk_factor: 风险因素（category: 1）
        - symptom: 症状（category: 2）
        - screening: 筛查方法（category: 3）
        """
        
        # 定义节点
        nodes = [
            # === 疾病节点 ===
            {"id": "lung_cancer", "name": "肺癌", "type": "disease", "category": 0, 
             "description": "起源于支气管黏膜或腺体的恶性肿瘤", "size": 60},
            
            {"id": "stomach_cancer", "name": "胃癌", "type": "disease", "category": 0,
             "description": "起源于胃黏膜上皮的恶性肿瘤", "size": 55},
            
            {"id": "liver_cancer", "name": "肝癌", "type": "disease", "category": 0,
             "description": "发生于肝脏的恶性肿瘤", "size": 55},
            
            {"id": "colorectal_cancer", "name": "结直肠癌", "type": "disease", "category": 0,
             "description": "结肠或直肠的恶性肿瘤", "size": 50},
            
            {"id": "breast_cancer", "name": "乳腺癌", "type": "disease", "category": 0,
             "description": "乳腺上皮组织的恶性肿瘤", "size": 50},
            
            # === 风险因素节点 ===
            {"id": "smoking", "name": "吸烟", "type": "risk_factor", "category": 1,
             "description": "首要致癌因素", "size": 50},
            
            {"id": "age_high", "name": "高龄", "type": "risk_factor", "category": 1,
             "description": "年龄>50岁", "size": 45},
            
            {"id": "genetic_risk", "name": "遗传因素", "type": "risk_factor", "category": 1,
             "description": "家族癌症史", "size": 45},
            
            {"id": "alcohol", "name": "饮酒", "type": "risk_factor", "category": 1,
             "description": "过量饮酒", "size": 40},
            
            {"id": "obesity", "name": "肥胖", "type": "risk_factor", "category": 1,
             "description": "BMI>28", "size": 40},
            
            {"id": "lack_exercise", "name": "缺乏运动", "type": "risk_factor", "category": 1,
             "description": "运动量<3小时/周", "size": 35},
            
            {"id": "unhealthy_diet", "name": "不良饮食", "type": "risk_factor", "category": 1,
             "description": "高盐、腌制、油炸食品", "size": 35},
            
            {"id": "chronic_hepatitis", "name": "慢性肝炎", "type": "risk_factor", "category": 1,
             "description": "乙肝、丙肝病史", "size": 40},
            
            # === 症状节点 ===
            {"id": "cough", "name": "持续咳嗽", "type": "symptom", "category": 2,
             "description": "咳嗽超过3周", "size": 30},
            
            {"id": "chest_pain", "name": "胸痛", "type": "symptom", "category": 2,
             "description": "胸部疼痛或不适", "size": 30},
            
            {"id": "weight_loss", "name": "体重下降", "type": "symptom", "category": 2,
             "description": "不明原因体重减轻", "size": 30},
            
            {"id": "stomach_pain", "name": "上腹痛", "type": "symptom", "category": 2,
             "description": "上腹部疼痛或不适", "size": 30},
            
            {"id": "fatigue", "name": "乏力", "type": "symptom", "category": 2,
             "description": "持续疲劳、无力", "size": 25},
            
            {"id": "blood_stool", "name": "便血", "type": "symptom", "category": 2,
             "description": "大便带血", "size": 30},
            
            # === 筛查方法节点 ===
            {"id": "ct_scan", "name": "低剂量CT", "type": "screening", "category": 3,
             "description": "肺癌筛查", "size": 35},
            
            {"id": "gastroscopy", "name": "胃镜检查", "type": "screening", "category": 3,
             "description": "胃癌筛查", "size": 35},
            
            {"id": "colonoscopy", "name": "肠镜检查", "type": "screening", "category": 3,
             "description": "结直肠癌筛查", "size": 35},
            
            {"id": "ultrasound", "name": "超声检查", "type": "screening", "category": 3,
             "description": "肝癌、乳腺癌筛查", "size": 35},
            
            {"id": "tumor_markers", "name": "肿瘤标志物", "type": "screening", "category": 3,
             "description": "血液检测", "size": 30}
        ]
        
        # 定义边（关系）
        edges = [
            # === 风险因素 → 疾病 ===
            {"source": "smoking", "target": "lung_cancer", "relation": "强相关", 
             "weight": 0.9, "lineStyle": {"color": "#ff4d4f", "width": 4}},
            
            {"source": "smoking", "target": "stomach_cancer", "relation": "增加风险",
             "weight": 0.5, "lineStyle": {"color": "#ff7875", "width": 2}},
            
            {"source": "age_high", "target": "lung_cancer", "relation": "增加风险",
             "weight": 0.7, "lineStyle": {"color": "#ffa940", "width": 3}},
            
            {"source": "age_high", "target": "stomach_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#ffa940", "width": 2}},
            
            {"source": "age_high", "target": "liver_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#ffa940", "width": 2}},
            
            {"source": "age_high", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.7, "lineStyle": {"color": "#ffa940", "width": 3}},
            
            {"source": "genetic_risk", "target": "lung_cancer", "relation": "增加风险",
             "weight": 0.7, "lineStyle": {"color": "#9254de", "width": 3}},
            
            {"source": "genetic_risk", "target": "breast_cancer", "relation": "强相关",
             "weight": 0.8, "lineStyle": {"color": "#9254de", "width": 4}},
            
            {"source": "genetic_risk", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#9254de", "width": 2}},
            
            {"source": "alcohol", "target": "liver_cancer", "relation": "强相关",
             "weight": 0.8, "lineStyle": {"color": "#ff4d4f", "width": 4}},
            
            {"source": "alcohol", "target": "stomach_cancer", "relation": "增加风险",
             "weight": 0.5, "lineStyle": {"color": "#ff7875", "width": 2}},
            
            {"source": "alcohol", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.5, "lineStyle": {"color": "#ff7875", "width": 2}},
            
            {"source": "obesity", "target": "breast_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#ffa940", "width": 2}},
            
            {"source": "obesity", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#ffa940", "width": 2}},
            
            {"source": "lack_exercise", "target": "breast_cancer", "relation": "增加风险",
             "weight": 0.5, "lineStyle": {"color": "#ffc069", "width": 2}},
            
            {"source": "lack_exercise", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.5, "lineStyle": {"color": "#ffc069", "width": 2}},
            
            {"source": "unhealthy_diet", "target": "stomach_cancer", "relation": "增加风险",
             "weight": 0.7, "lineStyle": {"color": "#ff7875", "width": 3}},
            
            {"source": "unhealthy_diet", "target": "colorectal_cancer", "relation": "增加风险",
             "weight": 0.6, "lineStyle": {"color": "#ff7875", "width": 2}},
            
            {"source": "chronic_hepatitis", "target": "liver_cancer", "relation": "强相关",
             "weight": 0.85, "lineStyle": {"color": "#ff4d4f", "width": 4}},
            
            # === 疾病 → 症状 ===
            {"source": "lung_cancer", "target": "cough", "relation": "常见症状",
             "weight": 0.8, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            {"source": "lung_cancer", "target": "chest_pain", "relation": "常见症状",
             "weight": 0.7, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            {"source": "lung_cancer", "target": "weight_loss", "relation": "常见症状",
             "weight": 0.6, "lineStyle": {"color": "#1890ff", "width": 1, "type": "dashed"}},
            
            {"source": "stomach_cancer", "target": "stomach_pain", "relation": "常见症状",
             "weight": 0.8, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            {"source": "stomach_cancer", "target": "weight_loss", "relation": "常见症状",
             "weight": 0.7, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            {"source": "liver_cancer", "target": "fatigue", "relation": "常见症状",
             "weight": 0.7, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            {"source": "liver_cancer", "target": "weight_loss", "relation": "常见症状",
             "weight": 0.6, "lineStyle": {"color": "#1890ff", "width": 1, "type": "dashed"}},
            
            {"source": "colorectal_cancer", "target": "blood_stool", "relation": "常见症状",
             "weight": 0.8, "lineStyle": {"color": "#1890ff", "width": 2, "type": "dashed"}},
            
            # === 疾病 → 筛查方法 ===
            {"source": "lung_cancer", "target": "ct_scan", "relation": "推荐筛查",
             "weight": 0.9, "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}},
            
            {"source": "stomach_cancer", "target": "gastroscopy", "relation": "推荐筛查",
             "weight": 0.9, "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}},
            
            {"source": "liver_cancer", "target": "ultrasound", "relation": "推荐筛查",
             "weight": 0.8, "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}},
            
            {"source": "liver_cancer", "target": "tumor_markers", "relation": "推荐筛查",
             "weight": 0.7, "lineStyle": {"color": "#52c41a", "width": 1, "type": "dotted"}},
            
            {"source": "colorectal_cancer", "target": "colonoscopy", "relation": "推荐筛查",
             "weight": 0.9, "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}},
            
            {"source": "breast_cancer", "target": "ultrasound", "relation": "推荐筛查",
             "weight": 0.8, "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}}
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "categories": [
                {"name": "疾病", "base": "disease"},
                {"name": "风险因素", "base": "risk_factor"},
                {"name": "症状", "base": "symptom"},
                {"name": "筛查方法", "base": "screening"}
            ]
        }
    
    def get_full_graph(self) -> Dict:
        """获取完整知识图谱"""
        return self.graph_data
    
    def get_user_risk_graph(self, user_data: Dict, assessment_result: Dict) -> Dict:
        """
        生成用户个性化风险图谱
        
        Args:
            user_data: 用户问卷数据
            assessment_result: 风险评估结果
            
        Returns:
            用户专属知识图谱
        """
        user_nodes = []
        user_edges = []
        
        # 1. 添加用户节点（中心节点）
        user_nodes.append({
            "id": "user",
            "name": "您",
            "type": "user",
            "category": 4,
            "size": 70,
            "symbolSize": 70,
            "itemStyle": {"color": "#1890ff"}
        })
        
        # 2. 根据用户数据添加风险因素
        risk_factors_map = {
            "smoking": ("smoking", "吸烟"),
            "age": ("age_high", "高龄") if user_data.get('age', 0) > 50 else None,
            "genetic_risk": ("genetic_risk", "遗传因素") if user_data.get('genetic_risk', 0) > 0 else None,
            "alcohol_intake": ("alcohol", "饮酒") if user_data.get('alcohol_intake', 0) > 2 else None,
            "bmi": ("obesity", "肥胖") if self._calculate_bmi(user_data) > 28 else None,
            "physical_activity": ("lack_exercise", "缺乏运动") if user_data.get('physical_activity', 5) < 3 else None
        }
        
        active_risk_factors = []
        for key, mapping in risk_factors_map.items():
            if mapping is None:
                continue
            
            factor_id, factor_name = mapping
            
            # 判断是否是用户的风险因素
            is_risk = False
            if key == "smoking" and user_data.get('smoking', 0) == 1:
                is_risk = True
            elif key in ["age", "genetic_risk", "alcohol_intake", "bmi", "physical_activity"] and mapping:
                is_risk = True
            
            if is_risk:
                user_nodes.append({
                    "id": factor_id,
                    "name": factor_name,
                    "type": "risk_factor",
                    "category": 1,
                    "size": 45
                })
                
                user_edges.append({
                    "source": "user",
                    "target": factor_id,
                    "relation": "具有风险因素",
                    "lineStyle": {"color": "#ff4d4f", "width": 2}
                })
                
                active_risk_factors.append(factor_id)
        
        # 3. 添加高风险疾病
        category_risks = assessment_result.get('category_risks', {})
        for cancer_name, risk_info in category_risks.items():
            risk_score = risk_info.get('score', 0)
            
            # 只显示中高风险以上的疾病
            if risk_score > 0.5:
                # 映射疾病名称到ID
                cancer_id_map = {
                    "肺癌": "lung_cancer",
                    "胃癌": "stomach_cancer",
                    "肝癌": "liver_cancer",
                    "结直肠癌": "colorectal_cancer",
                    "乳腺癌": "breast_cancer",
                    "前列腺癌": "prostate_cancer"
                }
                
                cancer_id = cancer_id_map.get(cancer_name)
                if cancer_id:
                    user_nodes.append({
                        "id": cancer_id,
                        "name": cancer_name,
                        "type": "disease",
                        "category": 0,
                        "size": 55,
                        "risk_score": risk_score
                    })
                    
                    # 连接风险因素到疾病
                    for factor_id in active_risk_factors:
                        # 查找知识图谱中的关系
                        for edge in self.graph_data['edges']:
                            if edge['source'] == factor_id and edge['target'] == cancer_id:
                                user_edges.append({
                                    "source": factor_id,
                                    "target": cancer_id,
                                    "relation": edge['relation'],
                                    "weight": edge['weight'],
                                    "lineStyle": edge.get('lineStyle', {})
                                })
        
        # 4. 添加推荐筛查
        for node in user_nodes:
            if node['type'] == 'disease':
                cancer_id = node['id']
                # 查找对应的筛查方法
                for edge in self.graph_data['edges']:
                    if edge['source'] == cancer_id and '筛查' in edge['relation']:
                        screening_id = edge['target']
                        # 查找筛查节点
                        screening_node = next(
                            (n for n in self.graph_data['nodes'] if n['id'] == screening_id),
                            None
                        )
                        if screening_node and screening_node['id'] not in [n['id'] for n in user_nodes]:
                            user_nodes.append({
                                **screening_node,
                                "size": 35
                            })
                            user_edges.append({
                                "source": cancer_id,
                                "target": screening_id,
                                "relation": "推荐筛查",
                                "lineStyle": {"color": "#52c41a", "width": 2, "type": "dotted"}
                            })
        
        return {
            "nodes": user_nodes,
            "edges": user_edges,
            "categories": self.graph_data['categories'] + [
                {"name": "用户", "base": "user"}
            ]
        }
    
    def _calculate_bmi(self, user_data: Dict) -> float:
        """计算BMI"""
        height = user_data.get('height', 170)
        weight = user_data.get('weight', 60)
        if height > 0:
            return weight / ((height / 100) ** 2)
        return 22.0


# 全局实例
knowledge_graph_service = KnowledgeGraphService()

