# GitLab API 命令参考

## 目录
- [环境准备](#环境准备)
- [项目查询](#项目查询)
- [仓库搜索](#仓库搜索)
- [文件与目录](#文件与目录)
- [提交历史](#提交历史)
- [分支操作](#分支操作)
- [MR 操作](#mr-操作)
- [Pipeline 操作](#pipeline-操作)

---

## 环境准备

```bash
BASE='https://gitlab.xylink.com/api/v4'
TOKEN=$(grep -E '^GITLAB_ACCESS_TOKEN=' ~/.xyinfpilot/.env | head -n1 | cut -d= -f2- | sed 's/^"//; s/"$//')
```

项目路径编码（python 辅助）：
```bash
PROJ='server%2Fbusi%2Fzz%2Fversion-resource'   # 手动编码
# 或
PROJ=$(python3 -c "import urllib.parse; print(urllib.parse.quote('group/sub/project', safe=''))")
```

---

## 项目查询

```bash
# 搜索我参与的项目
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects?membership=true&search=<kw>"

# 按路径获取项目信息（含 id、default_branch）
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ"
```

---

## 仓库搜索

### 代码搜索（blobs）

```bash
Q=$(python3 -c "import urllib.parse; print(urllib.parse.urlencode({'scope':'blobs','search':'<keyword>','ref':'<branch>','per_page':10}))")
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/search?$Q"
```

响应字段：`path`（文件路径）、`ref`（分支/commit）、`startline`、`data`（匹配片段）

### 提交搜索（commits）

```bash
Q=$(python3 -c "import urllib.parse; print(urllib.parse.urlencode({'scope':'commits','search':'<keyword>','ref':'<branch>','per_page':10}))")
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/search?$Q"
```

响应字段：`short_id`、`title`、`authored_date`

---

## 文件与目录

### 读取文件内容

```bash
# 文件路径需 URL 编码（/ → %2F）
FILE_ENC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('src/main/java/com/example/Foo.java', safe=''))")
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/repository/files/$FILE_ENC/raw?ref=<branch>"
```

### 目录树（递归）

```bash
Q=$(python3 -c "import urllib.parse; print(urllib.parse.urlencode({'ref':'<branch>','path':'src/main/java/com/example','recursive':'true','per_page':50}))")
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/repository/tree?$Q"
```

响应字段：`type`（blob/tree）、`path`、`name`

---

## 提交历史

### 按文件路径查提交

```bash
Q=$(python3 -c "import urllib.parse; print(urllib.parse.urlencode({'ref_name':'<branch>','path':'src/main/java/com/example/Foo.java','per_page':10}))")
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/repository/commits?$Q"
```

---

## 分支操作

```bash
# 列出所有分支
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/repository/branches?per_page=50"

# 查询特定分支
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/repository/branches/<branch_name>"
```

---

## MR 操作

```bash
# 列出 MR
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/merge_requests?state=opened"

# 创建 MR
curl -sS --request POST --header "PRIVATE-TOKEN: $TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"source_branch":"<src>","target_branch":"<target>","title":"<title>"}' \
  "$BASE/projects/$PROJ/merge_requests"
```

---

## Pipeline 操作

```bash
# 触发 Pipeline
curl -sS --request POST --header "PRIVATE-TOKEN: $TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"ref":"<branch>"}' \
  "$BASE/projects/$PROJ/pipeline"

# 查看 Pipeline 状态
curl -sS --header "PRIVATE-TOKEN: $TOKEN" "$BASE/projects/$PROJ/pipelines/<pipeline_id>"
```
