"""
数学练习题插件
"""

import sys
import os
sys.path.append('/aggregator')

import utils
from logger import logger


def crawl_math_exercises(params: dict):
    """
    抓取数学练习题
    
    Args:
        params: 插件参数
        
    Returns:
        抓取结果
    """
    logger.info(f"[MathExercisesPlugin] 开始抓取数学练习题，参数: {params}")
    
    base_url = params.get("base_url", "")
    grade = params.get("grade", "1")
    subject = params.get("subject", "math")
    
    # 模拟抓取逻辑
    results = []
    
    # 这里实现实际的抓取逻辑
    for i in range(5):
        results.append({
            "title": f"小学{grade}年级{subject}练习题{i+1}",
            "url": f"{base_url}/exercise_{i+1}.pdf",
            "subject": subject,
            "grade": grade,
            "type": "pdf",
            "push_to": ["math_exercises"]
        })
    
    logger.info(f"[MathExercisesPlugin] 抓取完成，共{len(results)}个练习题")
    return results


if __name__ == "__main__":
    # 测试函数
    test_params = {
        "base_url": "https://math-examples.com",
        "grade": "3",
        "subject": "math"
    }
    result = crawl_math_exercises(test_params)
    print(result)