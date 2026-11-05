# 清单与PDF成册

`scripts/build_packet.py` 负责排版、分类排序、A4纸张及页码索引，不理解票据的真实性、金额或适用政策。先按 SKILL.md 完成读取和核对，再传入 manifest。它不能取代附件1 Excel 的填写。

运行时需要 Python 3、pypdf、reportlab、Pillow 和可嵌入中文字体。脚本内置环境自举（若默认 `python3` 缺少依赖，会自动回退至本机已安装依赖的 Python 运行时）。Windows/macOS常见宋体可自动识别，也可 `--font` 指定 TTF/TTC。

```bash
python3 <skill目录>/scripts/build_packet.py <本次报销目录>/packet.json --output <本次报销目录>/output/v1
```

输出目录须为空或不存在，以免覆盖原件/旧版。若失败留下部分输出，检查报错后使用新版本目录重试。

## 输入格式

```json
{
  "title": "上海参会差旅材料核对",
  "itinerary": "成都 → 上海 → 成都；2026-10-12 至 2026-10-14，跨3个自然日；补助天数待确认",
  "note": "当前为待补草稿，住宿详情仍需补充。",
  "review_completed": false,
  "tasks": [
    {"id":"01","name":"去程票据","status":"received","evidence":"T001.pdf 第1页","note":"已读取时间、人物和地点"},
    {"id":"02","name":"住宿订单详情","status":"missing","action":"请提供入住/退房日期、人数、单价；可向酒店或平台索取","rule":"R09"}
  ],
  "documents": [
    {"id":"T001","title":"去程火车票","category":"transport","path":"originals/T001.pdf","pages":[1]},
    {"id":"P001","title":"支付记录","category":"payment","path":"originals/P001.png","label":"P001 对应 T001"}
  ]
}
```

- 路径相对 manifest 所在目录，或使用绝对路径。documents只列实际要入册的材料，不扫描整个目录，防止把规范文件、旧版、清单、无关证件等混进材料册。
- `tasks`：`received` 已收到、`generated` 已自动生成、`missing` 需补、`pending` 待确认、`na` 不适用。收到/生成需 `evidence`，补充/确认需 `action`，不适用需 `note` 说明。
- `documents.category` 只能是 `conference`、`transport`、`lodging`、`other`、`payment`；按上述顺序自动排序，同类保留传入顺序。行程单应紧随对应票据，在同类中顺序传入。页码从1开始，省略则纳入全部页。
- 支付记录必须给 `label`，以简短编号说明对应票据，在原内容下方空白处标注。完整明细放工作簿；长截图可按合理边界分成多页，先人工检查信息没有遗漏，不能为了塞一页缩到无法看清。
- 支持 PDF、PNG、JPG、JPEG、WEBP；其他格式先用合适工具转成PDF。交互PDF表单先导出已核对外观的打印副本；电子签名和可编辑原件另行保留。
- 对内容相同且页码相同的文件拒绝重复入册；同票不同截图仍须在识别阶段去重。一个支付记录关联多票时只入册一次，标注全部对应编号。
- `review_completed: true` 仅在所有适用要求和金额等均实际检查后填写。只要存在missing/pending，或未完成核对，材料册命名为“待补草稿”。这个布尔值不表示财务审核。
- `example: true` 只用于虚构展示，会在清单中明确写示例，不能用于真实报销。

## 输出与质量检查

- `材料核对清单.md` 与 `材料核对清单.pdf`：分状态列出已有材料、自动成果、具体补充动作。
- `报销材料册-待补草稿.pdf` 或 `报销材料册-待助理初审.pdf`：每个源页面各占一页A4；不插入辅助封面，不修改原件。无入册文件时不生成空材料册。
- `材料索引.json`：来源哈希、原页码、入册页码，可核对漏页与来源。

生成后渲染清单和材料册逐页查看可读性、完整性及方向；核对页数与索引。特别检查极长图片、横向票据、旋转PDF和二维码；A4尺寸正确不保证文字足够大。必要时改善源文件或重新分页后再交付。

若没有待补项，List显示0项待补但仍应明确“待助理初审”。缺少制度标准或未检查审批签字等不得仅靠清空tasks伪造材料齐全。
