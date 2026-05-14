#!/usr/bin/env bash
#
# install.sh — 把 backend tech_design schema 同步到当前业务服务仓库的 openspec
#
# 用法（在业务服务仓库根执行）：
#   bash <path-to-tech-spec>/plugins/dq-be-core/skills/dq-be-tech-design/openspec-schema/install.sh
#
# 默认从 GitLab main 分支拉取最新 schema；可用环境变量覆盖：
#   TECH_SPEC_REMOTE  — git remote URL（默认 git@gitlab.daqian369.com:esm/tech-spec.git）
#   TECH_SPEC_BRANCH  — 分支或 commit（默认 main）
#
# 动作（幂等）：
#   1. 检查 openspec/ 目录存在；若 openspec/config.yaml 缺失则兜底生成 spec-driven 版本
#   2. 若 openspec/schemas/backend/ 不存在，运行 openspec schema fork spec-driven backend
#   3. 用 git archive --remote 从 GitLab 拉取 schema.yaml 和 templates/tech_design.md
#   4. 覆盖到 openspec/schemas/backend/
#   5. 修改 openspec/config.yaml 的 schema: 字段为 backend
#   6. 运行 openspec schema validate backend
#   7. 扫 openspec/changes/ 下存量 change 的 .openspec.yaml，列出仍指向非 backend schema 的 change（仅提醒）
#
# 规范见 dq-be-tech-design skill（tech-spec 仓库）。

set -euo pipefail

REMOTE="${TECH_SPEC_REMOTE:-git@gitlab.daqian369.com:esm/tech-spec.git}"
BRANCH="${TECH_SPEC_BRANCH:-main}"
SCHEMA_PATH="plugins/dq-be-core/skills/dq-be-tech-design/openspec-schema"

# 当前仓库根（调用者的 cwd）
REPO_ROOT="$(pwd)"
OPENSPEC_DIR="${REPO_ROOT}/openspec"
OPENSPEC_CFG="${OPENSPEC_DIR}/config.yaml"
SCHEMA_DIR="${OPENSPEC_DIR}/schemas/backend"

echo "→ install.sh: remote = ${REMOTE} (${BRANCH})"
echo "→ install.sh: target repo = ${REPO_ROOT}"

# 1. 检查 openspec 已 init（存在 openspec/ 目录）；若 config.yaml 缺失则兜底创建
if [[ ! -d "${OPENSPEC_DIR}" ]]; then
  echo "✖ ${OPENSPEC_DIR} 不存在"
  echo "  请先在当前仓库运行 \`openspec init . --tools claude\` 初始化 openspec"
  exit 1
fi
if [[ ! -f "${OPENSPEC_CFG}" ]]; then
  echo "→ ${OPENSPEC_CFG} 不存在（可能是 openspec init 非交互模式未创建），兜底生成 spec-driven 版本"
  echo "schema: spec-driven" > "${OPENSPEC_CFG}"
fi

# 2. 确保 openspec/schemas/backend/ 存在（若无则 fork）
if [[ ! -d "${SCHEMA_DIR}" ]]; then
  echo "→ openspec/schemas/backend/ 不存在，fork spec-driven..."
  (cd "${REPO_ROOT}" && openspec schema fork spec-driven backend)
fi

# 3. 用 git archive --remote 从 GitLab 拉取 schema 文件
# 注意：部分 GitLab 实例默认关闭 git archive --remote 协议，若命令报错（exit 1 / "not found"）
# 可手动降级：克隆仓库后直接复制文件
#   git clone git@gitlab.daqian369.com:esm/tech-spec.git /tmp/tech-spec
#   cp /tmp/tech-spec/plugins/dq-be-core/skills/dq-be-tech-design/openspec-schema/schema.yaml openspec/schemas/backend/schema.yaml
#   cp /tmp/tech-spec/plugins/dq-be-core/skills/dq-be-tech-design/openspec-schema/templates/tech_design.md openspec/schemas/backend/templates/tech_design.md
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "→ 从 GitLab 拉取 schema（${BRANCH}）..."
git archive --remote="${REMOTE}" "${BRANCH}" \
  "${SCHEMA_PATH}/schema.yaml" \
  "${SCHEMA_PATH}/templates/tech_design.md" \
  | tar -x -C "${TMP_DIR}"

SRC_SCHEMA="${TMP_DIR}/${SCHEMA_PATH}/schema.yaml"
SRC_TEMPLATE="${TMP_DIR}/${SCHEMA_PATH}/templates/tech_design.md"

# 4. 覆盖 schema.yaml 和 templates/tech_design.md
mkdir -p "${SCHEMA_DIR}/templates"
cp "${SRC_SCHEMA}" "${SCHEMA_DIR}/schema.yaml"
cp "${SRC_TEMPLATE}" "${SCHEMA_DIR}/templates/tech_design.md"
echo "→ 已覆盖 schema.yaml 和 templates/tech_design.md"

# 5. 修改 config.yaml 的 schema: 字段
# 幂等实现：若已是 `schema: backend` 则跳过；若是其他值则替换；若无该字段则在文件开头插入
if grep -qE '^schema:\s*backend\s*$' "${OPENSPEC_CFG}"; then
  echo "→ config.yaml 已指向 backend schema，跳过"
elif grep -qE '^schema:\s*' "${OPENSPEC_CFG}"; then
  sed -i.bak -E 's|^schema:[[:space:]]*.+$|schema: backend|' "${OPENSPEC_CFG}"
  rm -f "${OPENSPEC_CFG}.bak"
  echo "→ 已修改 config.yaml 的 schema: 为 backend"
else
  printf 'schema: backend\n\n%s' "$(cat "${OPENSPEC_CFG}")" > "${OPENSPEC_CFG}.new"
  mv "${OPENSPEC_CFG}.new" "${OPENSPEC_CFG}"
  echo "→ 已在 config.yaml 顶部插入 schema: backend"
fi

# 6. 校验
echo "→ 校验 schema..."
(cd "${REPO_ROOT}" && openspec schema validate backend)

# 7. 扫存量 change：列出 .openspec.yaml 仍指向非 backend schema 的 change（仅提醒，不自动改）
CHANGES_DIR="${OPENSPEC_DIR}/changes"
if [[ -d "${CHANGES_DIR}" ]]; then
  NON_BACKEND_CHANGES=()
  while IFS= read -r f; do
    # 每个 change 的 .openspec.yaml；若 schema 行不是 backend 则纳入提醒
    if [[ -f "$f" ]] && ! grep -qE '^schema:[[:space:]]*backend[[:space:]]*$' "$f"; then
      NON_BACKEND_CHANGES+=("$(basename "$(dirname "$f")")")
    fi
  done < <(find "${CHANGES_DIR}" -maxdepth 2 -name ".openspec.yaml" 2>/dev/null)

  if (( ${#NON_BACKEND_CHANGES[@]} > 0 )); then
    echo ""
    echo "⚠ 以下 ${#NON_BACKEND_CHANGES[@]} 个 change 的 .openspec.yaml 仍指向非 backend schema。"
    echo "  若要走 backend 流程（含 tech_design artifact），请手动把 .openspec.yaml 里的 schema 字段改为 backend："
    for cid in "${NON_BACKEND_CHANGES[@]}"; do
      echo "    - ${cid}"
    done
    echo "  （存量 change 可能不需要 tech_design，故脚本不自动修改）"
  fi
fi

echo ""
echo "✔ 安装完成。下一次 \`openspec new <change-id>\` 会自动生成 tech_design.md。"
echo "  当前 change 目录：${REPO_ROOT}/openspec/changes/"
