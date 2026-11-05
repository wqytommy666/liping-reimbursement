# 丽萍姐报账 (`liping-reimbursement`)

> **电子科技大学视频通信与智能计算团队（AVC²）差旅报销整理与初审 Skill**  
> 把手头的行程、车票、发票、订单截图直接发给你的 Agent，由 **AVC² 团队助理丽萍姐** 自动帮你还原行程、把《附件1 报销材料清单》Excel、《附件2 出差车辆行驶登记表》Word 和《情况说明》全部填好、排好单张 A4 打印册，并配**例图**清楚告诉你还需要提供什么材料或信息。

![我是 AVC² 团队助理丽萍姐：还需你提供什么？](docs/丽萍报账-清单示例.png)

---

## 一、如何接入你的 Agent（全面支持国产与海外主流 Agent）

支持所有主流 **国产 AI Agent / AI IDE** 与 **海外 Agent 工具**：
- **国产 Agent**：**字节跳动 Trae / Trae CN**、**阿里 Qwen Code / 通义灵码**、**腾讯 CodeBuddy**、**百度文心快码 (Comate)**、**智谱 AutoGLM / 清言 Agent**、**月之暗面 Kimi CLI / 桌面端**、**DeepSeek Agent (結合 Cline / Roo Code / Cherry Studio)**、**豆包 MarsCode** 等。
- **海外 Agent**：**Codex**、**Claude Code**、**Antigravity (Gemini)**、**Cursor**、**Windsurf** 等。

### 方式 1：一键脚本接入全部 Agent（推荐）

打开终端（macOS / Linux 终端，或 Windows Git Bash / WSL）运行以下命令，会自动将 `liping-reimbursement` 接入本机所有主流国产与海外 Agent：

```bash
git clone https://github.com/wqytommy666/liping-reimbursement.git
cd liping-reimbursement
bash install.sh
```

### 方式 2：各款国产与海外 Agent 单独接入指南

如果你只想接入自己常用的某一款 Agent，也可以从 [Releases 页面](https://github.com/wqytommy666/liping-reimbursement/releases) 下载 `liping-reimbursement.zip` 解压，或按下方对应方式放入目录：

| Agent 名称 | 所属厂商 | 接入目录 / 配置方式 |
| --- | --- | --- |
| **Trae CN / Trae** | 字节跳动 | 全局放入 `~/.trae-cn/skills/liping-reimbursement`（或 `~/.trae/skills/liping-reimbursement`），或放入当前工作区 `.trae/skills/liping-reimbursement` |
| **Qwen Code / 通义灵码** | 阿里巴巴 | 全局放入 `~/.qwen/skills/liping-reimbursement`（或 `~/.tongyi/skills/liping-reimbursement`）；VS Code 插件版可在工作区添加 `.qwen/skills/liping-reimbursement` |
| **CodeBuddy** | 腾讯 | 全局放入 `~/.codebuddy/skills/liping-reimbursement`，或放入项目目录 `.codebuddy/skills/liping-reimbursement` |
| **文心快码 (Comate)** | 百度 | 全局放入 `~/.comate/skills/liping-reimbursement`，或在 Zulu 智能体「规则/技能」中导入 `skills/liping-reimbursement/SKILL.md` |
| **智谱 AutoGLM / GLM CLI** | 智谱 AI | 放入 `~/.glm/skills/liping-reimbursement` 或通用 `~/.agents/skills/liping-reimbursement` |
| **Kimi / DeepSeek (配 Cline / Roo Code)** | 月之暗面 / 深度求索 | 在 VS Code 的 Cline / Roo Code 中接入 DeepSeek-V3/R1 或 Kimi API，技能放入 `~/.cline/skills/liping-reimbursement` 或 `~/.roo/skills/liping-reimbursement` |
| **Cherry Studio / 豆包 / 纳米 AI 等桌面客户端** | 国产桌面端 | 打开本仓库，直接把 `skills/liping-reimbursement` 文件夹作为「工作区目录 / 本地知识库」挂载，并将 `SKILL.md` 设为助手提示词 |
| **Cursor / Windsurf** | 海外 AI IDE | 放入 `~/.cursor/skills/liping-reimbursement` 或 `~/.windsurf/skills/liping-reimbursement` |
| **Codex / Claude Code / Antigravity** | OpenAI / Anthropic / Google | 分别放入 `~/.codex/skills/`、`~/.claude/skills/`、`~/.gemini/config/skills/` |

> **Windows PowerShell 手动复制示例**（以字节 Trae CN 和阿里通义 Qwen 为例）：
> ```powershell
> git clone https://github.com/wqytommy666/liping-reimbursement.git
> New-Item -ItemType Directory -Force -Path "$HOME\.trae-cn\skills", "$HOME\.qwen\skills", "$HOME\.codebuddy\skills", "$HOME\.agents\skills"
> Copy-Item -Recurse -Force .\liping-reimbursement\skills\liping-reimbursement "$HOME\.trae-cn\skills\liping-reimbursement"
> Copy-Item -Recurse -Force .\liping-reimbursement\skills\liping-reimbursement "$HOME\.qwen\skills\liping-reimbursement"
> Copy-Item -Recurse -Force .\liping-reimbursement\skills\liping-reimbursement "$HOME\.codebuddy\skills\liping-reimbursement"
> Copy-Item -Recurse -Force .\liping-reimbursement\skills\liping-reimbursement "$HOME\.agents\skills\liping-reimbursement"
> ```

---

## 二、如何操作使用

接入完成后，**全程不需要你自己手动填 Excel 表格或写 Word 文档**——缺什么信息你直接在对话框里告诉 Agent，Agent 会帮你把表格和 Word 全部填好：

### 第 1 步：把现有票据放到一个文件夹，直接发给 Agent

把这次差旅手头已有的文件（车票 PDF、机票发票、酒店发票、水单、微信/支付宝账单截图、会议通知等）放进同一个文件夹，在对话框里直接说：

```text
丽萍姐，帮我报销这次差旅，行程和现有票据都在 /path/to/你的报销文件夹 里，你先帮我把表格和说明填好，再告诉我还差什么需要提供。
```

> 也可以在支持 `/` 或 `$` 的 Agent 里直接点名调用：`liping-reimbursement`

### 第 2 步：查看自动填好的表格/Word，按例图补交缺项或直接回复缺失信息

Agent 会自动从票据里提取信息，先把能填的表格和文档全部填好，并给你输出：
1. **已经帮你填好的文件**：
   - **《附件1-报销材料清单.xlsx》**（含“票据与支付明细”对账表）
   - 如涉及行程变更、邀请方承担食宿，自动帮你写好 **《情况说明》**
   - 如涉及自驾/租车，自动帮你填好 **《附件2-电子科技大学出差车辆行驶登记表.docx》**
   - 按团队要求顺序排好版的 **《报销材料册-待补草稿.pdf》**（单页单张 A4）
2. **核对清单 List（已收到 / 已帮你生成 / 还需要你提供）**：
   - 如果表格或 Word 里还缺某些文字信息（如**学号/工号、经费项目号、车牌号、往返里程、伙食补助标准**），你**不用自己打开 Excel 或 Word 去填**，直接在聊天框里把信息发给 Agent，Agent 会帮你填进表格和 Word 里。
3. **缺项对应例图**：如果还缺某项凭证（如酒店水单、支付记录、会议收费标准），Agent 会直接展示对应的**例图**，告诉你在哪下载、需要看清哪些字段。

### 第 3 步：把补充的材料或文字信息发给 Agent，生成最终打印版

把补好的截图放进文件夹，或者把缺失的信息直接回复给 Agent：

```text
丽萍姐，酒店水单我放进文件夹了；我的学号是 2025xxxx，报销项目号是 Y030xxxx，自驾车牌川Axxxxx、往返 120 公里，你帮我把 Excel 和附件2 Word 填好，更新一下最终打印册。
```

Agent 会把所有信息填入 **《附件1-报销材料清单.xlsx》**、**《附件2-电子科技大学出差车辆行驶登记表.docx》** 及 **《情况说明》**，并输出最终版 **《报销材料册-待助理初审.pdf》**，你直接打印签字即可。

---

## 三、AVC² 团队如何报账（报销要求与全流程）

### 1. 报销提交与时限要求
- **提交时限**：出差结束后 **15 个工作日内** 完成报销材料提交。
- **提交方式**：
  - **老师差旅**：可指定一名同学协助整理，当面提交给助理或发送电子版压缩包。
  - **学生差旅**：须整理好全部材料并打印签字后当面提交（可委托同学代交，但代交同学须清楚差旅具体情况）。
- **线下交件与预约**：
  1. 将排好版的 A4 材料册 **单面打印**，在需要签字的地方（情况说明、附件2等）本人签字。
  2. 微信联系 **AVC² 团队助理丽萍姐（袁丽萍，微信/电话：`18280174535`）** 预约提交时间。
  3. 按预约时间交至 **科研楼 B545**，同时将填好的 **《附件1-报销材料清单.xlsx》电子版** 发给丽萍姐微信。

### 2. 常见特殊情况怎么报账？
- **邀请方承担食宿**：**不需要找邀请方开具食宿承担证明**。报销时不申领对应的食宿费用，由 Agent 直接帮你写好一份《情况说明》（写明会议期间食宿由邀请方承担，本次不报销食宿费），打印出来本人签字即可。
- **单张发票超过 200 元**：凡单张发票票面金额 **严格大于 200 元**（200.00 元本身不需要），必须附微信/支付宝/银行卡支付记录截图。平台账单上收款方显示简称或带星号（如 `北京**服`）直接照收，无需展开全称。
- **自驾或租车出差**：把车牌号、往返里程等告诉 Agent，由 Agent 帮你填好内置的《附件2-电子科技大学出差车辆行驶登记表》Word 文档，附加油费/过路费发票及支付记录；注意**自驾或租车出差不发放市内交通补助**。
- **报销会议注册费**：需同时附上 **会议通知** + **含收费标准的页面** + **注册费发票** + **支付记录（>200元）**。
- **学生申报伙食补助**：需提供导师确认伙食补助标准的记录，并说明会议方是否提供餐饮。

### 3. 材料装订顺序与 17 类材料例图

所有材料按 **「会议通知 → 交通票据 → 住宿票据 → 其他票据 → 支付记录」** 顺序排列，普通材料每页单独占一张 A4（完整例图册见 [`docs/丽萍报账-材料图例手册.pdf`](docs/丽萍报账-材料图例手册.pdf)）：

| 序号 | 材料类型 | 内置例图 | 报账核对标准 |
| :---: | --- | --- | --- |
| 01 | 支付记录 | `payment-record.png` | 单张发票 >200 元必附，需含支付时间、金额、收款方；平台简称照收 |
| 02 | 支付与退款记录 | `refund-payment.png` | 合并支付或退票需附支付与退款截图，并注明对应票据 |
| 03 | 酒店水单 / 住宿明细 | `hotel-detail.png` | 发票未写明入住/退房日期、单价、天数时，向酒店或订房平台索取水单 |
| 04 | 住宿费发票 | `hotel-invoice.png` | 抬头：电子科技大学（税号 `121000004507193117`） |
| 05 | 火车票 / 铁路电子客票 | `rail-ticket.png` | 需看清乘车日期、起讫站、乘车人和票价 |
| 06 | 机票款发票 | `airfare-invoice.png` | 票面行程信息不全时需附平台或航司行程单 |
| 07 | 退票手续费发票 | `refund-fee-invoice.png` | 附退票手续费发票及对应退票记录 |
| 08 | 网约车 / 出租车行程单 | `taxi-itinerary.png` | 从出行平台导出，需有每段时间、起终点和费用 |
| 09 | 网约车 / 出租车发票 | `taxi-invoice.png` | 与网约车行程单金额一致 |
| 10 | 会议注册费发票 | `conference-fee-invoice.png` | 报销注册费时需同时附会议通知和注册费收费标准 |
| 11 | 行程变更情况说明 | `itinerary-change-note.png` | 往返路线不闭合、中转或改签退票时由 Agent 帮你写好，本人签字 |
| 12 | 会议通知 / 邀请函 | `conference-notice.png` | 含会议时间、地点和主办方 |
| 13 | 会议注册费收费标准 | `conference-fee-standard.png` | 国内/国际会议收费标准页，需能看清对应代表类别的金额 |
| 14 | 论文录用通知 | `paper-acceptance-notice.png` | 因论文录用参会报销时提供，含论文题目与录用结论 |
| 15 | 出差车辆行驶登记表（附件2） | `vehicle-registration-form.png` | 自驾/租车必填，把车牌和里程发给 Agent 即可帮你填好 Word 表 |
| 16 | 邀请方承担食宿情况说明 | `host-covered-lodging-note.png` | **不用对方开证明**，报销时不报销食宿，由 Agent 写好说明、本人签字 |
| 17 | 其余按需补充事项 | `no-source-examples.png` | 导师/经费项目确认、实际收款方不一致盖章说明、航司行程单等 |

---

## 四、仓库目录结构

```text
liping-reimbursement/
├── README.md
├── install.sh
├── LICENSE
├── docs/
│   ├── 丽萍报账-清单示例.png
│   ├── 丽萍报账-清单示例.pdf
│   └── 丽萍报账-材料图例手册.pdf
└── skills/
    └── liping-reimbursement/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── assets/
        │   ├── 差旅报销通知-2026-10-28.pdf
        │   ├── 附件1-报销材料清单.xlsx
        │   ├── 附件2-电子科技大学出差车辆行驶登记表.docx
        │   ├── example.json
        │   └── material-examples/
        │       ├── catalog.json
        │       └── *.png
        ├── references/
        │   ├── example.md
        │   ├── material-examples.md
        │   ├── packet.md
        │   ├── policy.md
        │   └── template-map.md
        └── scripts/
            ├── build_packet.py
            └── test_build_packet.py
```

## 许可证

MIT License，详见 [LICENSE](LICENSE)。
