#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/skills/liping-reimbursement"

if [ ! -d "$SKILL_SRC" ]; then
  echo "未找到 $SKILL_SRC，请在 liping-reimbursement 仓库根目录下运行本脚本。"
  exit 1
fi

# 核心安装目录
mkdir -p "$HOME/.agents/skills"
rm -rf "$HOME/.agents/skills/liping-reimbursement"
cp -R "$SKILL_SRC" "$HOME/.agents/skills/liping-reimbursement"

# 自动同步到国内外主流 Agent 的技能目录
AGENT_SKILL_DIRS=(
  "$HOME/.trae/skills"              # 字节跳动 Trae (国际版)
  "$HOME/.trae-cn/skills"           # 字节跳动 Trae CN (国内版)
  "$HOME/.qwen/skills"              # 阿里 Qwen Code / 通义灵码
  "$HOME/.tongyi/skills"            # 阿里通义灵码本地技能目录
  "$HOME/.codebuddy/skills"         # 腾讯 CodeBuddy AI IDE
  "$HOME/.comate/skills"            # 百度文心快码 Comate
  "$HOME/.glm/skills"               # 智谱清言 / AutoGLM CLI
  "$HOME/.deepseek/skills"          # DeepSeek CLI / 社区 Agent
  "$HOME/.kimi/skills"              # 月之暗面 Kimi CLI / Agent
  "$HOME/.cline/skills"             # Cline / Roo Code
  "$HOME/.roo/skills"               # Roo Code
  "$HOME/.cursor/skills"            # Cursor
  "$HOME/.windsurf/skills"          # Windsurf
  "$HOME/.codex/skills"             # OpenAI Codex
  "$HOME/.claude/skills"            # Anthropic Claude Code
  "$HOME/.gemini/config/skills"     # Google Antigravity / Gemini CLI
)

for dir in "${AGENT_SKILL_DIRS[@]}"; do
  mkdir -p "$dir"
  ln -sfn "$HOME/.agents/skills/liping-reimbursement" "$dir/liping-reimbursement"
done

echo "✅ 「丽萍姐报账 (liping-reimbursement)」已成功接入你的本机 Agent 环境！"
echo "   已覆盖：Trae CN / 通义灵码(Qwen) / 腾讯 CodeBuddy / 文心快码 / 智谱 GLM / Kimi / DeepSeek / Cline / Roo Code / Cursor / Codex / Claude Code / Antigravity"
