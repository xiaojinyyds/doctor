#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
B2B升级测试脚本
测试新增的功能是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录（获取Token）"""
    print("\n=== 测试登录 ===")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "account": "doctor@xiehe.com",
            "password": "admin123"
        }
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return data["data"]["access_token"]
    return None


def test_doctor_pending_list(token):
    """测试医生工作台-待审核列表"""
    print("\n=== 测试待审核列表 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/doctor/pending-assessments",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")


def test_doctor_statistics(token):
    """测试医生工作台统计"""
    print("\n=== 测试医生工作台统计 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/doctor/statistics",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")


def main():
    """主测试流程"""
    print("="*60)
    print("B2B升级功能测试")
    print("="*60)
    
    # 1. 登录获取Token
    token = test_login()
    if not token:
        print("\n❌ 登录失败，请检查数据库中是否有测试账号")
        print("提示：执行 backend/my.sql 中的测试数据插入语句")
        return
    
    print(f"\n✅ 登录成功，Token: {token[:50]}...")
    
    # 2. 测试医生工作台
    test_doctor_pending_list(token)
    test_doctor_statistics(token)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()
