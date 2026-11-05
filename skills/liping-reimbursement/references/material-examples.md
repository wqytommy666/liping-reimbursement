# 缺什么，就展示对应图片

图例来自用户的历史报销材料。只遮姓名和身份证号，其他信息保留。每次展示最相关的1至3张，每张配一两句，具体字段见 `assets/material-examples/catalog.json`。

| 缺项 | 图片（相对技能目录） | 简短提示 |
| --- | --- | --- |
| 支付记录 | assets/material-examples/payment-record.png | 发支付详情截图，有时间、金额、收款方即可；平台简称可接受。 |
| 合并支付/退款 | assets/material-examples/refund-payment.png | 发支付和退款截图，注明对应哪些票据。 |
| 酒店水单/住宿明细 | assets/material-examples/hotel-detail.png | 向酒店或订房平台要入住日期、单价、天数等明细。 |
| 住宿发票 | assets/material-examples/hotel-invoice.png | 提供房费发票；没写住宿详情的配水单或订单。 |
| 火车票 | assets/material-examples/rail-ticket.png | 提供能看到乘车日期、起讫站和乘车人的票据。 |
| 机票款发票 | assets/material-examples/airfare-invoice.png | 提供机票发票；行程信息不足时补平台行程单。 |
| 退票手续费发票 | assets/material-examples/refund-fee-invoice.png | 提供手续费发票及对应退票记录。 |
| 网约车行程单 | assets/material-examples/taxi-itinerary.png | 从出行平台获取有时间、起终点和费用的行程单。 |
| 网约车发票 | assets/material-examples/taxi-invoice.png | 提供发票，并与行程单对应。 |
| 注册费发票 | assets/material-examples/conference-fee-invoice.png | 向收费方要发票，参会通知和收费标准另附。 |
| 行程变更说明 | assets/material-examples/itinerary-change-note.png | 助手按真实行程起草，本人核实签名；本图为原文重排。 |
| 会议通知/邀请函 | assets/material-examples/conference-notice.png | 提供含会议时间、地点和主办方的会议通知或邀请函。 |
| 会议注册费收费标准 | assets/material-examples/conference-fee-standard.png | 报销注册费时附收费标准，能看清对应代表类型的收费金额。 |
| 论文录用通知 | assets/material-examples/paper-acceptance-notice.png | 因论文录用参会或报销相关费用时，提供含论文题目与录用结论的通知。 |
| 出差车辆行驶登记表（附件2） | assets/material-examples/vehicle-registration-form.png | 自驾或租车报销时填写（已内置 `assets/附件2-电子科技大学出差车辆行驶登记表.docx`，助手可预填）。 |
| 邀请方承担食宿情况说明 | assets/material-examples/host-covered-lodging-note.png | 邀请方承担食宿不用证明，报销时不报销食宿就行，由助手自动起草情况说明并由本人签名。 |
| 其余按需补充事项 | assets/material-examples/no-source-examples.png | 仅在涉及且缺失时展示（导师/项目确认、收款方不一致盖章说明、航司行程单/审批表）。 |

例如：“还缺酒店水单，向酒店要一份住宿明细即可，参考下图。”随后直接嵌入 `hotel-detail.png`。

收款方显示简称或星号的原截图照常接受，不要求展开全称，不把简称当作收款方不一致。邀请方承担食宿不用证明，报销时不报销对应食宿并由助手起草情况说明即可。只有实际金额、订单等存在矛盾时才询问具体问题。

图例不能替代当前凭证；不混入当次材料册或费用计算。原文档只用于本地处理，分享版使用平面图片，姓名含手写姓名及开票人姓名，身份证号含已部分隐藏的号码。其他字段按用户要求保留。

导师/项目确认、商家盖章说明、航司官方行程单和完整审批表暂未提供固定样图；不伪造这些材料。机票款发票不当作航司官方行程单，注册费发票不当作会议通知。
