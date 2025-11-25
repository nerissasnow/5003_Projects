# myapp/templatetags/custom_filter.py
from django import template
import math  # 确保导入math模块

register = template.Library()

# 修复1：重命名函数避免递归
@register.filter
def absolute_value(value):
    """返回绝对值 - 使用不同的函数名避免递归"""
    try:
        # 使用Python内置的abs函数，不是递归调用自己
        return abs(value)  # 这会调用Python内置的abs函数
    except (TypeError, ValueError):
        return value

# 修复2：确保get_expiry_status使用正确的函数
@register.filter
def get_expiry_status(value):
    """根据天数返回过期状态"""
    if value is None:
        return "unknown"
    
    # 使用修复后的absolute_value函数
    abs_value = absolute_value(value)
    
    if value < 0:  # 使用原始值判断正负
        return "expired"
    elif abs_value <= 7:  # 使用绝对值判断天数
        return "urgent"
    elif abs_value <= 30:
        return "soon"
    else:
        return "good"

@register.filter
def get_status_class(value):
    """根据状态返回CSS类名"""
    status_map = {
        "good": "status-good",
        "soon": "status-soon", 
        "urgent": "status-urgent",
        "expired": "status-expired",
        "unknown": "status-unknown"
    }
    return status_map.get(value, "status-unknown")

@register.filter
def get_status_text(value):
    """根据状态返回显示文本"""
    status_map = {
        "good": "Good",
        "soon": "Expiring Soon", 
        "urgent": "Urgent",
        "expired": "Expired",
        "unknown": "Unknown"
    }
    return status_map.get(value, "Unknown")

# 添加一个更安全的abs过滤器替代方案
@register.filter(name='abs')  # 在模板中仍可使用'abs'名称
def abs_filter(value):
    """安全的abs过滤器，使用内置函数"""
    try:
        return abs(value)  # 调用Python内置abs
    except (TypeError, ValueError):
        return value