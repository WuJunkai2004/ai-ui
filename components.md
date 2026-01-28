# UI 组件协议文档

本文档详细描述了 GenUI 系统支持的 10 种 UI 组件类型。
包括 `/api/v1/analyze` 接口返回的组件结构定义，以及用户在前端交互后，提交给 `/api/v1/execute` 接口的数据格式。

---

## 通用字段 (Base Component)

所有组件对象都包含以下基础字段：

*   `id` (string): 组件的唯一标识符，用于在提交数据时作为 Key。
*   `type` (string): 组件类型名称（见下文）。
*   `label` (string): 显示给用户的标题或标签。
*   `description` (string, 可选): 辅助说明文字。

---

## 1. Input (文本输入框)

用于收集单行文本信息，如姓名、城市、关键词等。

### `/analyze` 返回结构
```json
{
  "id": "destination",
  "type": "Input",
  "label": "目的地",
  "placeholder": "例如：巴黎",
  "default_value": "北京", // 可选
  "description": "请输入您想去的城市" // 可选
}
```

### `/execute` 提交格式 (`form_data`)
提交字符串值。
```json
{
  "destination": "巴黎"
}
```

---

## 2. Select (单选下拉框)

用于从预定义的选项中选择一项。

### `/analyze` 返回结构
```json
{
  "id": "trip_type",
  "type": "Select",
  "label": "旅行类型",
  "options": [
    { "label": "休闲度假", "value": "leisure" },
    { "label": "商务出行", "value": "business" },
    { "label": "探险", "value": "adventure" }
  ],
  "default_value": "leisure" // 可选
}
```

### `/execute` 提交格式
提交选中项的 `value`。
```json
{
  "trip_type": "business"
}
```

---

## 3. DatePicker (日期/日期范围选择器)

用于选择具体日期或时间段。

### `/analyze` 返回结构
```json
{
  "id": "travel_dates",
  "type": "DatePicker",
  "label": "出行日期",
  "range": true // true表示选择范围，false表示选择单日
}
```

### `/execute` 提交格式
*   **单日模式**: ISO 8601 格式字符串。
*   **范围模式**: 包含开始和结束日期的数组。

```json
// 单日
{ "travel_dates": "2023-10-01" }

// 范围
{ "travel_dates": ["2023-10-01", "2023-10-07"] }
```

---

## 4. MultiSelect (多选下拉/标签)

用于从预定义选项中选择多项。

### `/analyze` 返回结构
```json
{
  "id": "interests",
  "type": "MultiSelect",
  "label": "兴趣偏好",
  "options": [
    { "label": "美食", "value": "food" },
    { "label": "博物馆", "value": "museum" },
    { "label": "购物", "value": "shopping" }
  ],
  "default_values": ["food"] // 可选
}
```

### `/execute` 提交格式
提交包含选中 `value` 的数组。
```json
{
  "interests": ["food", "museum"]
}
```

---

## 5. Button (按钮/确认动作)

通常用于确认表单或触发特定动作。在表单场景下，通常作为提交触发器，或者作为独立的布尔标记。

### `/analyze` 返回结构
```json
{
  "id": "confirm_booking",
  "type": "Button",
  "label": "立即预订",
  "action": "submit_booking",
  "variant": "primary" // primary, secondary, danger 等
}
```

### `/execute` 提交格式
通常提交该按钮是否被点击，或点击时携带的特定 Action 标识。
```json
{
  "confirm_booking": "submit_booking"
}
```

---

## 6. MapPin (地图选点)

用于在地图上选择精确的地理位置。

### `/analyze` 返回结构
```json
{
  "id": "meeting_point",
  "type": "MapPin",
  "label": "集合地点",
  "default_lat": 39.9042, // 可选
  "default_lng": 116.4074 // 可选
}
```

### `/execute` 提交格式
包含经纬度的对象。
```json
{
  "meeting_point": {
    "lat": 39.9087,
    "lng": 116.3975
  }
}
```

---

## 7. RangeSlider (范围滑块)

用于选择数值范围（如价格区间、时间长度）。

### `/analyze` 返回结构
```json
{
  "id": "budget",
  "type": "RangeSlider",
  "label": "预算范围",
  "min": 0,
  "max": 10000,
  "step": 100, // 可选，默认1
  "unit": "CNY", // 可选
  "default_min": 1000, // 可选
  "default_max": 5000 // 可选
}
```

### `/execute` 提交格式
包含最小值和最大值的数组 `[min, max]`。
```json
{
  "budget": [2000, 8000]
}
```

---

## 8. VisualPicker (视觉选择器)

用于通过图片进行选择（如装修风格、商品款式）。

### `/analyze` 返回结构
```json
{
  "id": "style_pref",
  "type": "VisualPicker",
  "label": "选择装修风格",
  "multi_select": false,
  "options": [
    {
      "image_url": "https://example.com/modern.jpg",
      "value": "modern",
      "label": "现代简约"
    },
    {
      "image_url": "https://example.com/classic.jpg",
      "value": "classic",
      "label": "古典欧式"
    }
  ]
}
```

### `/execute` 提交格式
*   **单选**: 选中项的 `value`。
*   **多选**: `value` 的数组。

```json
{
  "style_pref": "modern"
}
```

---

## 9. Stepper (步进器)

用于选择数量（如人数、房间数）。

### `/analyze` 返回结构
```json
{
  "id": "guest_count",
  "type": "Stepper",
  "label": "入住人数",
  "min": 1,
  "max": 10,
  "step": 1,
  "default_value": 2
}
```

### `/execute` 提交格式
提交具体的数字。
```json
{
  "guest_count": 3
}
```

---

## 10. Switch (开关)

用于布尔值选择（是/否）。

### `/analyze` 返回结构
```json
---

## 综合示例 (End-to-End Example)

### 步骤 1：`/analyze` 返回 (AI 认为需要收集信息)

**场景**: 用户说 "我想买个手机"

```json
{
    "components": [
        {
            "id": "budget",
            "label": "预算",
            "type": "RangeSlider",
            "min": 1000.0,
            "max": 15000.0,
            "unit": "CNY"
        },
        {
            "id": "os",
            "label": "操作系统偏好",
            "type": "Select",
            "options": [
                { "label": "iOS (苹果)", "value": "ios" },
                { "label": "Android (安卓)", "value": "android" },
                { "label": "无所谓", "value": "any" }
            ]
        },
        {
            "id": "brands",
            "label": "品牌偏好",
            "type": "MultiSelect",
            "options": [
                { "label": "Apple", "value": "apple" },
                { "label": "华为", "value": "huawei" },
                { "label": "小米", "value": "xiaomi" }
            ]
        },
        {
            "id": "features",
            "label": "主要关注点",
            "type": "MultiSelect",
            "options": [
                { "label": "拍照", "value": "camera" },
                { "label": "游戏性能", "value": "gaming" },
                { "label": "续航", "value": "battery" }
            ]
        }
    ],
    "message": ""
}
```

### 步骤 2：`/execute` 请求 (用户填写后的提交)

当前端收集完用户在上述 UI 中的输入后，发送给后端的请求体如下：

```json
{
    "original_query": "我想买个手机",
    "form_data": {
        "budget": [3000, 6000],
        "os": "android",
        "brands": ["huawei", "xiaomi"],
        "features": ["camera", "battery"]
    }
}
```

**解析**:
1. `budget`: 对应 `RangeSlider`，提交的是包含两个数值的数组。
2. `os`: 对应 `Select`，提交的是选中的单个字符串 `value`。
3. `brands`: 对应 `MultiSelect`，提交的是选中的 `value` 字符串数组。
4. `features`: 同样对应 `MultiSelect`，提交的是字符串数组。
